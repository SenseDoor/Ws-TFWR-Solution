# === 主调度器 ===
# 纯调度，零业务参数
# 所有业务决策由 TaskCenter 内部根据 Config 配置决定

import TaskCenter

def main():
	clear()

	# 初始化任务中心
	TaskCenter.init()

	# 创建所有配置的任务
	TaskCenter.create_all_tasks()

	# 分发所有任务到执行器
	TaskCenter.dispatch_all()

	# 主无人机监控循环
	while True:
		TaskCenter.monitor()

main()
