import grm

game = grm.Game()

game.player_join(grm.Player(2))
game.player_join(grm.Player(2))

game.player_init_mixed_strategies()

"""
Matching Pennies game
Bimatrix:
    [1, -1],
    [-1, 1]

    [-1, 1],
    [1, -1],
the unique NE at (0.5, 0.5)
"""
# player 1
game.player_assign_payoff(1, "11", 1)
game.player_assign_payoff(1, "12", -1)
game.player_assign_payoff(1, "21", -1)
game.player_assign_payoff(1, "22", 1)
# player 2
game.player_assign_payoff(2, "11", -1)
game.player_assign_payoff(2, "12", 1)
game.player_assign_payoff(2, "21", 1)
game.player_assign_payoff(2, "22", -1)

# run the iterations to approximate Nash equilibrium
game.run()

# visulize the game evolution for `grm.Player(3)`
game.plot_2()
