# 仓库 PR 审核与合并对比 · 历史数据验收示例

统计日期 2026-11-25，UTC。来源为用户提供的 GitHub 查询历史快照，抓取分钟未记录。为复现原例，使用指定创建周 2026-10-26 至 11-01；全仓结案窗口为 10-26 至 11-24（均含首尾）。开放数为当日快照。以下派工是使用这些数字的模拟决策。

Mooncake 同批 93 个合格外部 PR 中有 34 个在两周内合并。LMCache 已合并的 34 个 PR 中位用时最短，首评样本中仍有一半未见正式评审。若只有一个 CPU 槽位，近期审核活跃程度相近时，它适合先投入低成本复核。

| 仓库 | 外部 PR 在 14 天内合并 | 已合并者的用时中位数 | 首次人工正式评审 | 当前全仓开放 PR |
| --- | --- | --- | --- | --- |
| [kvcache-ai/Mooncake](https://github.com/kvcache-ai/Mooncake/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 36.6%（34/93） | 3.15 天（36 项） | 7/12 有首评，中位 11.8 小时 | 700 |
| [vllm-project/vllm](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 30.6%（300/981） | 3.58 天（366 项） | 6/12 有首评，中位 11.6 小时 | 8,077 |
| [LMCache/LMCache](https://github.com/LMCache/LMCache/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 28.8%（30/104） | 1.48 天（34 项） | 6/12 有首评，中位 9.5 小时 | 743 |
| [NVIDIA/TensorRT-LLM](https://github.com/NVIDIA/TensorRT-LLM/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 23.8%（15/63） | 5.70 天（20 项） | 9/12 有首评，中位 129.7 小时 | 1,295 |
| [sgl-project/sglang](https://github.com/sgl-project/sglang/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 19.7%（152/771） | 3.70 天（180 项） | 1/12 有首评，实际等待 541.8 小时 | 6,360 |
| [deepseek-ai/DeepInfer](https://github.com/deepseek-ai/DeepInfer/pulls?q=is%3Apr+created%3A2026-10-26..2026-11-01) | 0.0%（0/25） | 无已合并样本 | 2/12 有首评，中位 10.7 小时 | 239 |

## 本轮派工（演练）

设本轮仅有一个 CPU agent 槽位，可用 GPU 为零。交付时所有实际分配均为 0，下表展示交付后完成一次模拟派工的状态。候选、设备约束和停止指令均为假设。

| 仓库 | 候选方向 | 优先级 | 本轮实际分配的 agent/设备 | 排队原因 | 下次重排条件 |
| --- | --- | --- | --- | --- | --- |
| Mooncake | 传输 benchmark 的双卡对照 | 第二 | 0 / 0 | 14 天比例 36.6% 居首，当前验证需要两张空闲卡 | 获准的两张卡可同时使用 |
| vLLM | 指标计数边界 | 待核实 | 0 / 0 | 类似修复可能已在上游 | 查明实现范围 |
| LMCache | 用 CPU trace 复核计数 | 第一 | 1 个 agent / CPU，0 GPU | 可立刻验证，人工反馈中位 9.5 小时 | 得到实验结果或收到维护者反馈 |
| TensorRT-LLM | 通信策略对照 | 等设备 | 0 / 0 | 无适配设备 | 硬件及编译环境就绪 |
| SGLang | 调度顺序回归 | 候补 | 0 / 0 | 唯一 CPU 槽位已用，抽查仅 1/12 有首评 | 槽位释放或维护者明确邀测 |
| DeepInfer | 图像输入兼容性 | 已停止 | 0 / 0 | 用户叫停，已退出队列 | 用户明确恢复 |

## 近 30 天全仓结案对照

| 仓库 | 合并 M | 关闭未合并 C | 结案合并率 | 查询 |
| --- | --- | --- | --- | --- |
| kvcache-ai/Mooncake | 362 | 28 | 92.8%（362/390） | [合并](https://github.com/kvcache-ai/Mooncake/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/kvcache-ai/Mooncake/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/kvcache-ai/Mooncake/pulls?q=is%3Apr+is%3Aopen) |
| vllm-project/vllm | 2,430 | 388 | 86.2%（2430/2818） | [合并](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/vllm-project/vllm/pulls?q=is%3Apr+is%3Aopen) |
| LMCache/LMCache | 352 | 32 | 91.7%（352/384） | [合并](https://github.com/LMCache/LMCache/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/LMCache/LMCache/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/LMCache/LMCache/pulls?q=is%3Apr+is%3Aopen) |
| NVIDIA/TensorRT-LLM | 1,129 | 84 | 93.1%（1129/1213） | [合并](https://github.com/NVIDIA/TensorRT-LLM/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/NVIDIA/TensorRT-LLM/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/NVIDIA/TensorRT-LLM/pulls?q=is%3Apr+is%3Aopen) |
| sgl-project/sglang | 2,440 | 492 | 83.2%（2440/2932） | [合并](https://github.com/sgl-project/sglang/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/sgl-project/sglang/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/sgl-project/sglang/pulls?q=is%3Apr+is%3Aopen) |
| deepseek-ai/DeepInfer | 5 | 1 | 83.3%（5/6） | [合并](https://github.com/deepseek-ai/DeepInfer/pulls?q=is%3Apr+is%3Amerged+merged%3A2026-10-26..2026-11-24) · [关闭未合并](https://github.com/deepseek-ai/DeepInfer/pulls?q=is%3Apr+is%3Aclosed+is%3Aunmerged+closed%3A2026-10-26..2026-11-24) · [开放](https://github.com/deepseek-ai/DeepInfer/pulls?q=is%3Apr+is%3Aopen) |

## 历史样本与复算边界

原例按外部 PR 号排序，以随机种子 20261125 抽取 12 项，括号内为首评等待小时数；其余为当时未见符合口径的正式评审。下列编号固定该次样本。上方创建和状态查询可复查，实时开放数会变化。历史汇总没有完整逐项排除清单与原始响应；新任务按现行口径留存快照，使用 SHA-256 稳定抽样。

- kvcache-ai/Mooncake　[#4936](https://github.com/kvcache-ai/Mooncake/pull/4936) · [#5033](https://github.com/kvcache-ai/Mooncake/pull/5033)（307.9 h） · [#5060](https://github.com/kvcache-ai/Mooncake/pull/5060) · [#5088](https://github.com/kvcache-ai/Mooncake/pull/5088) · [#5016](https://github.com/kvcache-ai/Mooncake/pull/5016)（10.9 h） · [#4944](https://github.com/kvcache-ai/Mooncake/pull/4944) · [#5078](https://github.com/kvcache-ai/Mooncake/pull/5078)（11.8 h） · [#5052](https://github.com/kvcache-ai/Mooncake/pull/5052)（0.4 h） · [#5003](https://github.com/kvcache-ai/Mooncake/pull/5003)（64.2 h） · [#5117](https://github.com/kvcache-ai/Mooncake/pull/5117)（49.8 h） · [#5070](https://github.com/kvcache-ai/Mooncake/pull/5070) · [#4971](https://github.com/kvcache-ai/Mooncake/pull/4971)（7.0 h）
- vllm-project/vllm　[#64885](https://github.com/vllm-project/vllm/pull/64885)（11.4 h） · [#64981](https://github.com/vllm-project/vllm/pull/64981) · [#63639](https://github.com/vllm-project/vllm/pull/63639)（11.7 h） · [#64102](https://github.com/vllm-project/vllm/pull/64102) · [#64293](https://github.com/vllm-project/vllm/pull/64293) · [#64466](https://github.com/vllm-project/vllm/pull/64466) · [#64003](https://github.com/vllm-project/vllm/pull/64003) · [#65012](https://github.com/vllm-project/vllm/pull/65012)（195.1 h） · [#63694](https://github.com/vllm-project/vllm/pull/63694)（0.2 h） · [#64403](https://github.com/vllm-project/vllm/pull/64403)（25.1 h） · [#64214](https://github.com/vllm-project/vllm/pull/64214) · [#63907](https://github.com/vllm-project/vllm/pull/63907)（8.1 h）
- LMCache/LMCache　[#6046](https://github.com/LMCache/LMCache/pull/6046)（47.2 h） · [#6127](https://github.com/LMCache/LMCache/pull/6127)（1.1 h） · [#6154](https://github.com/LMCache/LMCache/pull/6154)（10.6 h） · [#6175](https://github.com/LMCache/LMCache/pull/6175) · [#6100](https://github.com/LMCache/LMCache/pull/6100) · [#6052](https://github.com/LMCache/LMCache/pull/6052)（3.6 h） · [#6168](https://github.com/LMCache/LMCache/pull/6168) · [#6144](https://github.com/LMCache/LMCache/pull/6144) · [#6090](https://github.com/LMCache/LMCache/pull/6090)（23.7 h） · [#6202](https://github.com/LMCache/LMCache/pull/6202) · [#6161](https://github.com/LMCache/LMCache/pull/6161)（8.4 h） · [#6221](https://github.com/LMCache/LMCache/pull/6221)
- NVIDIA/TensorRT-LLM　[#21341](https://github.com/NVIDIA/TensorRT-LLM/pull/21341)（8.8 h） · [#21363](https://github.com/NVIDIA/TensorRT-LLM/pull/21363)（403.5 h） · [#20981](https://github.com/NVIDIA/TensorRT-LLM/pull/20981)（4.0 h） · [#21139](https://github.com/NVIDIA/TensorRT-LLM/pull/21139) · [#21166](https://github.com/NVIDIA/TensorRT-LLM/pull/21166) · [#21246](https://github.com/NVIDIA/TensorRT-LLM/pull/21246)（129.7 h） · [#21083](https://github.com/NVIDIA/TensorRT-LLM/pull/21083)（10.4 h） · [#20987](https://github.com/NVIDIA/TensorRT-LLM/pull/20987)（1.7 h） · [#21215](https://github.com/NVIDIA/TensorRT-LLM/pull/21215) · [#21163](https://github.com/NVIDIA/TensorRT-LLM/pull/21163)（213.0 h） · [#21044](https://github.com/NVIDIA/TensorRT-LLM/pull/21044)（136.8 h） · [#21285](https://github.com/NVIDIA/TensorRT-LLM/pull/21285)（208.7 h）
- sgl-project/sglang　[#46494](https://github.com/sgl-project/sglang/pull/46494) · [#47041](https://github.com/sgl-project/sglang/pull/47041) · [#47281](https://github.com/sgl-project/sglang/pull/47281) · [#47454](https://github.com/sgl-project/sglang/pull/47454) · [#46880](https://github.com/sgl-project/sglang/pull/46880) · [#46539](https://github.com/sgl-project/sglang/pull/46539)（541.8 h） · [#47400](https://github.com/sgl-project/sglang/pull/47400) · [#47191](https://github.com/sgl-project/sglang/pull/47191) · [#46789](https://github.com/sgl-project/sglang/pull/46789) · [#47666](https://github.com/sgl-project/sglang/pull/47666) · [#47337](https://github.com/sgl-project/sglang/pull/47337) · [#46669](https://github.com/sgl-project/sglang/pull/46669)
- deepseek-ai/DeepInfer　[#232](https://github.com/deepseek-ai/DeepInfer/pull/232)（14.0 h） · [#243](https://github.com/deepseek-ai/DeepInfer/pull/243) · [#247](https://github.com/deepseek-ai/DeepInfer/pull/247) · [#250](https://github.com/deepseek-ai/DeepInfer/pull/250) · [#240](https://github.com/deepseek-ai/DeepInfer/pull/240) · [#233](https://github.com/deepseek-ai/DeepInfer/pull/233) · [#249](https://github.com/deepseek-ai/DeepInfer/pull/249) · [#245](https://github.com/deepseek-ai/DeepInfer/pull/245) · [#237](https://github.com/deepseek-ai/DeepInfer/pull/237)（7.4 h） · [#248](https://github.com/deepseek-ai/DeepInfer/pull/248) · [#254](https://github.com/deepseek-ai/DeepInfer/pull/254) · [#252](https://github.com/deepseek-ai/DeepInfer/pull/252)
