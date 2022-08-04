import grm

game = grm.Game()

# four palyers, each uses two, three, four, and five pure strategies
game.player_join(grm.Player(2))
game.player_join(grm.Player(3))
game.player_join(grm.Player(4))
game.player_join(grm.Player(5))

game.player_init_mixed_strategies()

# set the payoff
game.player_assign_random_payoff()

# run the iterations to approximate Nash equilibrium
game.run()
