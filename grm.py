import numpy as np
import sys
import random
import itertools


class Player(object):
    def __init__(self, pure_strategies_num):
        pure_strategies_num = int(pure_strategies_num)
        if pure_strategies_num < 2:
            print(
                "ERROR: %s cannot be the number of strategies per player"
                % pure_strategies_num
            )
            sys.exit(1)
        self.pure_strategies_num = pure_strategies_num
        self.regret_sum_l = []
        self.path_l = []
        self.payoff_vector = None

    def assign_random_payoff(self, po_min=-1000, po_max=1000):
        pool = np.arange(po_min, po_max)
        self.payoff_vector = np.random.choice(pool, self.game.product_space_size)

    def assign_payoff(self, combi_str, payoff):
        if self.payoff_vector is None:
            self.payoff_vector = np.zeros(self.game.product_space_size)
        combi_index = self.game.get_strategy_combination_index(combi_str)
        self.payoff_vector[combi_index] = payoff

    def __vector_update(self, a, b, r):
        a = a + r * b
        a = a / a.sum()  # transform it to point in simplex
        return a

    def __randomize_mixed_strategy(self, n, str_max=100):
        pool = np.arange(1, str_max)
        str_ = np.random.choice(pool, n)
        str_ = str_ / str_.sum()
        str_ = str_.round(4)
        str_[0] += 1 - str_.sum()  # in case the sum doesn't add up to the whole one
        return str_.astype(np.float64)

    def init_mixed_strategies(self, init_strategies=None):
        if init_strategies is None:
            self.mixed_strategy = self.__randomize_mixed_strategy(
                self.pure_strategies_num
            )
        else:
            if len(init_strategies) == self.pure_strategies_num:
                self.mixed_strategy = np.array(init_strategies).astype(np.float64)
            else:
                print(
                    "Error: player %s with %s pures initialized to %s"
                    % (self.id, self.pure_strategies_num, init_strategies)
                )
                sys.exit(1)

    def run_one_iteration(self, rate, player_index):
        """the core of everything
        time complexity: (n-1)g^n multiplications,
        where g is the average of players' pure strategies number
        """
        # step 1: evalute vertex payoff vector: \vec{v}
        v = []
        for j in np.arange(self.pure_strategies_num):
            vertex_prob_dist = self.game.compute_joint_dist_on_vertex(player_index, j)
            a_vertex_payoff = vertex_prob_dist.dot(self.payoff_vector)
            v.append(a_vertex_payoff)

        # step 2: compute payoff
        payoff = self.mixed_strategy.dot(v)

        # step 3: compute regret_vector
        temp = v - payoff
        self.regret_vector = np.where(temp > 0, temp, 0)

        # step 4: collect stats: regret_sum and path
        self.regret_sum_l.append(self.regret_vector.sum())
        self.path_l.append(self.mixed_strategy)

        # step 5: update strategies
        self.mixed_strategy = self.__vector_update(
            self.mixed_strategy, self.regret_vector, rate
        )


class Game(object):
    def __init__(self):
        self.players = []
        self.players_num = 0
        self.fig_dpi = 50
        self.pure_product_space = None

    def player_join(self, player):
        if self.pure_product_space is None:
            player.game = self
            player.id = self.players_num + 1
            self.players.append(player)
            self.players_num += 1
        else:
            print("ERORR: cannot join new players any more")
            sys.exit(1)

    def player_assign_random_payoff(self):
        self.__build_product_space_of_pures()
        for player in self.players:
            player.assign_random_payoff()
        print("Payoff functions were randomized")

    def player_assign_payoff(self, player_index, combi_str, payoff):
        self.__build_product_space_of_pures()
        # player index starts from 0, and hence minus 1
        player = self.players[player_index - 1]
        player.assign_payoff(combi_str, payoff)

    def get_strategy_combination_index(self, combi_str):
        # this will be a terrible searching
        for i, combi in enumerate(self.pure_product_space):
            # strategy index starts from 1, and hence add 1
            combi_str_inside = "".join(str(x + 1) for x in combi)
            if combi_str == combi_str_inside:
                return i

    def player_init_mixed_strategies(self, init_strategies=None):
        if init_strategies is None:
            # random
            for player in self.players:
                player.init_mixed_strategies()
            print("Initial strategies were randomized")
        else:
            # custom
            if len(init_strategies) != self.players_num:
                print(
                    "Error: %s players is given %s initial strategies"
                    % (self.players_num, len(init_strategies))
                )
                sys.exit(1)
            for i, player in enumerate(self.players):
                player.init_mixed_strategies(init_strategies[i])
            print("Initial strategies were customized")

    def __build_product_space_of_pures(self):
        """
        create a list of tuples, each of which is the form of, e.g.
            ordered (0, 2, 1, ...), where each entry represents the index of pure strategy.
        each tuple can be seen as a combination of pure strategies.
        all the tuples in the list form the product space of all players' pure strateges.
        """
        if self.pure_product_space is not None:
            # product space was built
            return
        temp_l = []
        if self.players_num < 2:
            print("ERROR: %s player, no game" % self.players_num)
            sys.exit(1)
        for player in self.players:
            temp_l.append(set(range(player.pure_strategies_num)))
        self.pure_product_space = list(itertools.product(*temp_l))
        self.product_space_size = len(self.pure_product_space)

    def compute_joint_dist_on_vertex(self, player_index, pure_strategy_index):
        """
        return the probability dist, which is computed when
        1. the player on `player_index` changes the probability to 1 (hence on the "vertex" of simplex)
            for the pure strategy on `pure_strategy_index`.
        2. meanwhile, the other players keep theirs unchanged.
        index i: for player
        index j: for pure strategies of player i
        index k: for the combination of pure strategies in `pure_product_space` and `prob_dict`
        time complexity: (n-1)g^(n-1) multiplications
        """
        prob_dist = np.zeros(self.product_space_size)
        for k, combi in enumerate(self.pure_product_space):
            # ignore those combination without `pure_strategy_index` in it,
            # leaving its prob. slot in `prob_dist` to zero
            if combi[player_index] != pure_strategy_index:
                continue
            prob = 1
            # there are g^(n-1) combinations surviving here
            for i, j in enumerate(combi):
                if i == player_index and j == pure_strategy_index:
                    # equivalent to multiplying by 1, which is the vertex prob.
                    pass
                else:
                    # real deal: there are n-1 multiplications
                    prob *= self.players[i].mixed_strategy[j]
            prob_dist[k] = prob
        return prob_dist

    def __show_eqpt(self, eqpt):
        regret_sum_l = []
        print(
            "=========== Nash Equilibrium Approximation: %s iterations ============"
            % self.iterations
        )
        for i, (mixed, regret_vector) in enumerate(zip(eqpt[0], eqpt[1])):
            regret_sum_l.append(regret_vector.sum())
            print(
                "Player %s:" % (i + 1),
                "Nash Eq.",
                mixed.round(4).tolist(),
                "Deviation",
                regret_vector.round(4).tolist(),
            )
        regret_sum_a = np.array(regret_sum_l).round(4)
        print(
            "Deviation Sum:",
            *regret_sum_a,
            "Overall: %s" % np.round(regret_sum_a.sum(), 4)
        )

    def plot_2(self):
        # if any player is not using two pure strategies, quit plotting
        for player in self.players:
            if np.array(player.path_l).shape[1] != 2:
                print("ERROR: at least one player is not using TWO pure strategies")
                sys.exit(1)

        try:
            import matplotlib.pyplot as plt
        except:
            print("ERROR: you haven't installed matplotlib packages")
            sys.exit(1)

        plt.figure(figsize=(16, 8))
        ax = plt.gca()

        for player in self.players:
            xy = np.array(player.path_l)
            ax.plot(xy[:, 0], alpha=1, zorder=2)

        plt.tight_layout()
        self.__random_diagram_file_name()
        plt.savefig(self.plot_file_name, bbox_inches="tight", dpi=self.fig_dpi)
        plt.show()

    def __barycentric_to_cartesian(self, strategy_a):
        """transform simplex on R^3 into a triangle on R^2"""
        barycentric_x = np.array([0, np.sqrt(2) / 2, np.sqrt(2)]).T
        barycentric_y = np.array([0, np.sqrt(6) / 2, 0]).T
        return strategy_a.dot(barycentric_x), strategy_a.dot(barycentric_y)

    def plot_3(self):
        # if any player uses less than three pure strategies, quit plotting
        for player in self.players:
            if np.array(player.path_l).shape[1] != 3:
                print("ERROR: at least one player is not using THREE pure strategies")
                sys.exit(1)
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as mpatches
        except:
            print("ERROR: you haven't installed matplotlib packages")
            sys.exit(1)

        plt.figure(figsize=(8, 8))
        ax = plt.gca()
        triangle = mpatches.Polygon(
            np.array([[0, 0], [np.sqrt(2) / 2, np.sqrt(6) / 2], [np.sqrt(2), 0]]),
            fc="gray",
            alpha=0.1,
        )
        ax.add_artist(triangle)

        plt.axis("scaled")
        plt.xlim(0, np.sqrt(2))
        plt.ylim(0, np.sqrt(6) / 2)

        for player in self.players:
            x_a, y_a = self.__barycentric_to_cartesian(np.array(player.path_l))
            ax.plot(x_a, y_a, alpha=0.5, zorder=2)

        plt.tight_layout()
        self.__random_diagram_file_name()
        plt.savefig(self.plot_file_name, bbox_inches="tight", dpi=self.fig_dpi)
        plt.show()

    def __random_diagram_file_name(self):
        samples = "abcdefghijklmnopqrstuvwxyz"
        samples = samples + samples.upper() + "0123456789"
        self.plot_file_name = "./game_" + "".join(random.sample(samples, 6)) + ".png"
        print("Plot diagram: " + self.plot_file_name)

    def run(self, iterations=10**4 * 6, rate=10**-5):
        """run iterations"""
        # show initial strategy
        print("Initial strategies of all %s players:" % self.players_num)
        for _, player in enumerate(self.players):
            print("%s," % player.mixed_strategy.round(4).tolist())

        # regularize the payoff to [-1000, 1000] for accuracy
        # because payoff matrix X has the same Nash Eq. as aX+b
        for player in self.players:
            pv = player.payoff_vector
            interval = pv.max() - pv.min()
            if interval > 0:
                a = 2000 / interval
                b = 1000 - a * pv.max()
                pv = a * pv + b
                player.payoff_vector = pv
            else:
                player.payoff_vector.fill(1000)

        # here goes the iteration
        self.iterations = iterations
        regret_sum_overall_old = 10**10  # super big number to start with
        for _ in range(iterations):
            """time complexity: n(n-1)g^n multiplications
            multiprocessing would be nice here, supposedly reducing O(n^2g^n) to O(ng^n)
            """
            for i, player in enumerate(self.players):
                player.run_one_iteration(rate, i)

            regret_sum_overall_cur = np.sum(
                [p.regret_vector.sum() for p in self.players]
            )
            # if this is a new minimum
            if regret_sum_overall_cur < regret_sum_overall_old:
                strategy_path_l = [p.mixed_strategy for p in self.players]
                regret_sum_l = [p.regret_vector for p in self.players]
                regret_sum_overall_old = regret_sum_overall_cur

        self.__show_eqpt([strategy_path_l, regret_sum_l])


if __name__ == "__main__":
    pass
