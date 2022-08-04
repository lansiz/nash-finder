import grm

game = grm.Game()

# two playeys, and each player uses THREE pure strategies
game.player_join(grm.Player(3))
game.player_join(grm.Player(3))

game.player_init_mixed_strategies()

"""
Shapley Rock-Paper-Scissor game
Bimatrix:
    [0, 0, 1],
    [1, 0, 0],
    [0, 1, 0]

    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 0],
the unique NE at (1/3, 1/3, 1/3)
"""
# player 1
game.player_assign_payoff(1, "11", 0)
game.player_assign_payoff(1, "12", 0)
game.player_assign_payoff(1, "13", 1)
game.player_assign_payoff(1, "21", 1)
game.player_assign_payoff(1, "22", 0)
game.player_assign_payoff(1, "23", 0)
game.player_assign_payoff(1, "31", 0)
game.player_assign_payoff(1, "32", 1)
game.player_assign_payoff(1, "33", 0)
# player 2
game.player_assign_payoff(2, "11", 0)
game.player_assign_payoff(2, "12", 1)
game.player_assign_payoff(2, "13", 0)
game.player_assign_payoff(2, "21", 0)
game.player_assign_payoff(2, "22", 0)
game.player_assign_payoff(2, "23", 1)
game.player_assign_payoff(2, "31", 1)
game.player_assign_payoff(2, "32", 0)
game.player_assign_payoff(2, "33", 0)

# run the iterations to approximate Nash equilibrium
game.run()

# visulize the game evolution for `grm.Player(3)`
game.plot_3()
