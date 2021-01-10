
def fill_empty_starters(order_starters):
	for i in range(len(order_starters)):
		if order_starters[i] == "":
			player_info = {}
			player_info['player'] = ''

			position = ''
			
			if i == 0:
				position = 'QB'
			elif i == 1 or i == 2:
				position = 'RB'
			elif i == 3 or i == 4:
				position = 'WR'
			elif i == 5:
				position = 'TE'
			elif i == 6:
				position = 'FLEX'
			elif i == 7:
				position = 'DEF'
			elif i == 8:
				position = 'K'

			player_info['table_position'] = position
			order_starters[i] = player_info

	return order_starters