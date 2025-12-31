# === 默认执行器 ===
# 彩蛋执行器：当任务类型未知时，随机执行一个有趣的动作

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
# zone 参数为兼容接口，默认执行器不使用区域
def run(task_id, zone):
	# 随机选一个彩蛋动作执行
	r = random()
	if r < 0.2:
		_action_flip()
	elif r < 0.4:
		_action_pet()
	elif r < 0.6:
		_action_wizard_hat()
	elif r < 0.8:
		_action_pumpkin_hat()
	else:
		_action_cone()
