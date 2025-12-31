# === 主调度器 ===
# 纯调度，零业务参数
# 所有业务决策由 TaskCenter 内部根据 Config 配置决定

import TaskCenter

def main():
	clear()

	# 初始化任务中心
	TaskCenter.init()

	# 主无人机监控循环（动态生成任务）
	while True:
		TaskCenter.monitor()

main()
