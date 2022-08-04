import grm

game = grm.Game()

# three palyers, and each player use TWO pure strategies
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))

game.player_init_mixed_strategies()
# game.player_init_mixed_strategies([
#     [0.5, 0.5],
#     [0.5, 0.5],
#     [0.5, 0.5],
#     ])

# assign the payoff (define the payoff function)
# player 1
# left matrix
game.player_assign_payoff(1, "111", 4)
game.player_assign_payoff(1, "121", 3)
game.player_assign_payoff(1, "211", 5)
game.player_assign_payoff(1, "221", 5)
# right matrix
game.player_assign_payoff(1, "112", 4)
game.player_assign_payoff(1, "122", 5)
game.player_assign_payoff(1, "212", 8)
game.player_assign_payoff(1, "222", 4)

# player 2
# left matrix
game.player_assign_payoff(2, "111", 5)
game.player_assign_payoff(2, "121", 2)
game.player_assign_payoff(2, "211", 3)
game.player_assign_payoff(2, "221", 4)
# right matrix
game.player_assign_payoff(2, "112", 6)
game.player_assign_payoff(2, "122", 3)
game.player_assign_payoff(2, "212", 2)
game.player_assign_payoff(2, "222", 3)

# player 3
# left matrix
game.player_assign_payoff(3, "111", 3)
game.player_assign_payoff(3, "121", 5)
game.player_assign_payoff(3, "211", 2)
game.player_assign_payoff(3, "221", 4)
# right matrix
game.player_assign_payoff(3, "112", 2)
game.player_assign_payoff(3, "122", 4)
game.player_assign_payoff(3, "212", 6)
game.player_assign_payoff(3, "222", 5)

# run the iterations to approximate Nash equilibrium
game.run()

# visulize the game evolution for `grm.Player(2)`
game.plot_2()
