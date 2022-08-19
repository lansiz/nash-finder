import grm

game = grm.Game()

# six palyers, each uses two pure strategies
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))
game.player_join(grm.Player(2))


# run the iterations to approximate Nash equilibrium
while True:
    game.player_init_mixed_strategies()
    game.player_assign_random_payoff()
    game.run()
    game.plot_2()
    print()
