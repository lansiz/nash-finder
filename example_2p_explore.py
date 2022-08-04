import grm

game = grm.Game()

# two playeys, and each player uses THREE pure strategies
game.player_join(grm.Player(3))
game.player_join(grm.Player(3))

# assign the payoff (define the payoff function)
# player 1
game.player_assign_payoff(1, "11", -231)
game.player_assign_payoff(1, "12", -505)
game.player_assign_payoff(1, "13", 525)
game.player_assign_payoff(1, "21", -552)
game.player_assign_payoff(1, "22", 831)
game.player_assign_payoff(1, "23", -928)
game.player_assign_payoff(1, "31", -74)
game.player_assign_payoff(1, "32", -96)
game.player_assign_payoff(1, "33", -604)
# player 2
game.player_assign_payoff(2, "11", 175)
game.player_assign_payoff(2, "12", -350)
game.player_assign_payoff(2, "13", -770)
game.player_assign_payoff(2, "21", -641)
game.player_assign_payoff(2, "22", -222)
game.player_assign_payoff(2, "23", -189)
game.player_assign_payoff(2, "31", 302)
game.player_assign_payoff(2, "32", 504)
game.player_assign_payoff(2, "33", 767)

init_strategy_1 = [
    [0.4593, 0.314, 0.2267],
    [0.1698, 0.217, 0.6132],
]
init_strategy_2 = [
    [0.3818, 0.0182, 0.6],
    [0.3125, 0.5375, 0.15],
]

game.player_init_mixed_strategies(init_strategy_1)
game.run()

print()

game.player_init_mixed_strategies(init_strategy_2)
game.run()

# while True:
#     game.player_init_mixed_strategies()
#     game.run()
