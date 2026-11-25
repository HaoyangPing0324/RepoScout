"""Initialize a private SMTP config or notify its owner about one review package."""

import argparse
import os
import smtplib
import ssl
import stat
import sys
from email.headerregistry import Address
from email.message import EmailMessage
from pathlib import Path

TEMPLATE = """# RepoScout 邮件通知：用自己的邮箱给自己发审核提醒。
# 打开邮箱服务商的帮助或账户设置，找到“邮件客户端 / SMTP 发信”设置。
# 将值直接填在等号右侧，每行一项，不加引号。以 # 开头的行是说明。
#
# 发件服务器：填写服务商列出的 SMTP 主机名，例如 Gmail 填 smtp.gmail.com。
SMTP_HOST=

# 端口和加密方式成对填写。服务商标注 STARTTLS 通常用 587 + starttls，
# 标注 SSL/TLS 通常用 465 + ssl。以下预填的是第一种组合。
SMTP_PORT=587
SMTP_SECURITY=starttls

# 登录名：通常是完整邮箱地址，例如 yourname@gmail.com。
SMTP_USER=

# 登录凭据：在邮箱的安全设置中为邮件客户端生成“授权码”或“应用专用密码”，
# 把生成的值填在下一行。以 Gmail 为例，启用两步验证且账户支持时，可前往
# https://myaccount.google.com/apppasswords 创建。请仅在本机文件中填写。
SMTP_PASSWORD=

# 收发通知的邮箱：填你自己能查看的完整地址，通常和 SMTP_USER 相同。
SMTP_ADDRESS=
"""


class DeliveryUncertain(Exception):
    """A transport failure occurred during submission."""


class ConfigError(ValueError):
    """A message safe to show without exposing settings."""


def initialize(path):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("SMTP config already exists; retained.")
        return
    with os.fdopen(fd, "w", encoding="utf-8") as config:
        config.write(TEMPLATE)
    print("Private SMTP config created.")


def read_settings(path):
    with path.open(encoding="utf-8") as config:
        info = os.fstat(config.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid():
            raise ConfigError("Use an owner-only regular file (mode 0600).")
        settings = {}
        for line in config:
            if line.strip() and not line.lstrip().startswith("#"):
                key, separator, value = line.rstrip("\r\n").partition("=")
                if not separator or key in settings:
                    raise ConfigError("Malformed or duplicate SMTP setting.")
                settings[key] = value
    for key in ("HOST", "PORT", "SECURITY", "USER", "PASSWORD", "ADDRESS"):
        if not settings.get("SMTP_" + key):
            raise ConfigError("Missing SMTP_" + key)
    if settings["SMTP_SECURITY"] not in {"ssl", "starttls"}:
        raise ConfigError("SMTP_SECURITY must be ssl or starttls.")
    return settings


def send(settings, args):
    try:
        address = Address(addr_spec=settings["SMTP_ADDRESS"])
        port = int(settings["SMTP_PORT"])
        if not address.domain or not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise ConfigError("Invalid SMTP_ADDRESS or SMTP_PORT.") from None
    message = EmailMessage()
    message["From"] = message["To"] = address
    message["Subject"] = f"[RepoScout] 待审核 {args.repo} / {args.candidate}"
    message.set_content(
        f"仓库：{args.repo}\n候选：{args.candidate}\n版本：{args.revision}\n"
        f"审核材料：{args.review_dir.resolve(strict=True)}\n"
        "请查看 PR.md、ISSUE.md、REVIEW.md 和 REQUIREMENTS.md，再告知审核决定。"
    )
    context = ssl.create_default_context()
    host = settings["SMTP_HOST"]
    if settings["SMTP_SECURITY"] == "ssl":
        client = smtplib.SMTP_SSL(host, port, timeout=20, context=context)
    else:
        client = smtplib.SMTP(host, port, timeout=20)
    try:
        if settings["SMTP_SECURITY"] == "starttls":
            client.starttls(context=context)
        client.login(settings["SMTP_USER"], settings["SMTP_PASSWORD"])
        try:
            client.send_message(message, from_addr=address.addr_spec, to_addrs=[address.addr_spec])
        except (smtplib.SMTPServerDisconnected, TimeoutError, ConnectionError) as error:
            raise DeliveryUncertain from error
        except smtplib.SMTPException:
            raise
        except OSError as error:
            raise DeliveryUncertain from error
    finally:
        client.close()
    print("SMTP accepted the review notification.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path, nargs="?", default=Path("smtp.env"),
                        help="SMTP config path (default: smtp.env in the working directory)")
    parser.add_argument("--init", action="store_true")
    parser.add_argument("--repo")
    parser.add_argument("--candidate")
    parser.add_argument("--revision")
    parser.add_argument("--review-dir", type=Path)
    args = parser.parse_args()
    if args.init:
        initialize(args.config)
        return
    if not all((args.repo, args.candidate, args.revision, args.review_dir)):
        parser.error("Sending requires --repo, --candidate, --revision and --review-dir.")
    for name in ("PR.md", "ISSUE.md", "REVIEW.md", "REQUIREMENTS.md"):
        if not (args.review_dir / name).is_file():
            raise ConfigError(f"Review package lacks {name}.")
    send(read_settings(args.config), args)


if __name__ == "__main__":
    try:
        main()
    except DeliveryUncertain:
        print("Delivery uncertain. Check the inbox before retrying.", file=sys.stderr)
        sys.exit(3)
    except ConfigError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
    except (OSError, ValueError, smtplib.SMTPException) as error:
        # Server replies and parser exceptions can contain user-provided secrets.
        print(f"Notification setup or delivery failed ({type(error).__name__}).", file=sys.stderr)
        sys.exit(1)
