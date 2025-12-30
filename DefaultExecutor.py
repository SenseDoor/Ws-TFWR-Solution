# === 默认执行器 ===
# 彩蛋执行器：当任务类型未知时，随机执行一个有趣的动作

import TaskCenter

# 彩蛋动作
def _action_flip():
	do_a_flip()

def _action_pet():
	pet_the_piggy()

def _action_wizard_hat():
	change_hat(Hats.Wizard_Hat)

def _action_pumpkin_hat():
	change_hat(Hats.Pumpkin_Hat)

def _action_cone():
	change_hat(Hats.Traffic_Cone)

# 默认执行器：执行单一随机彩蛋
def run(task_id):
	task = TaskCenter.get_task(task_id)
	if task != None:
		print("Unknown task type: " + task["type"])

	# 随机选一个彩蛋动作执行
	actions = [_action_flip, _action_pet, _action_wizard_hat, _action_pumpkin_hat, _action_cone]
	action_index = int(random() * len(actions))
	actions[action_index]()

	TaskCenter.complete_task(task_id)
