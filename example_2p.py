import grm

game = grm.Game()

# two playeys, and each player uses THREE pure strategies
game.player_join(grm.Player(3))
game.player_join(grm.Player(3))

game.player_init_mixed_strategies()

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

# run the iterations to approximate Nash equilibrium
game.run(iterations=10**4 * 6)

# visulize the game evolution for `grm.Player(3)`
game.plot_3()
