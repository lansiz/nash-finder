import numpy as np
import sys
import random
import itertools


class Player(object):
    def __init__(self, pure_strategies_num):
        self.pure_strategies_num = pure_strategies_num
        self.regret_sum_l = []
        self.path_l = []
        self.payoff_vector = None

    def assign_random_payoff(self, product_space_size, po_min=-1000, po_max=1000):
        pool = np.arange(po_min, po_max)
        self.payoff_vector = np.random.choice(pool, product_space_size).astype(
            np.float64
        )

    def assign_payoff(self, product_space_size, combi_index, value):
        if self.payoff_vector is None:
            self.payoff_vector = np.zeros(product_space_size).astype(np.float64)
        self.payoff_vector[combi_index] = value

    def vector_update(self, a, b, r):
        a = a + r * b
        a = a / a.sum()  # transform it to point in simplex
        # a = a / np.linalg.norm(a)  # transform it to unit vector
        return a

    def randomize_mixed_strategy(self, n, str_max=100):
        """prepare the initial strategies and the str_max parameter
        decides how 'skew' the prob. proportion is.
        """
        pool = np.arange(1, str_max)
        str_ = np.random.choice(pool, n)
        str_ = str_ / str_.sum()
        str_ = str_.round(4)
        str_[0] += 1 - str_.sum()
        return str_.astype(np.float64)

    def init_mixed_strategies(self):
        self.mixed_strategy = self.randomize_mixed_strategy(self.pure_strategies_num)

    def run_one_iteration(self, game, rate, player_index):
        """the core of everything
        time complexity: (n-1)g^n multiplications,
        where g is the average of players' pure strategies number
        """

        # step 1: evalute vertex payoff vector: \vec{v}
        v = []
        for j in np.arange(self.pure_strategies_num):
            vertex_prob_dist = game.compute_joint_dist_on_vertex(player_index, j)
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
        self.mixed_strategy = self.vector_update(self.mixed_strategy, self.regret_vector, rate)


class Game(object):
    def __init__(self):
        self.players = []
        self.players_num = 0
        self.fig_dpi = 50
        self.pure_product_space = None

    def player_join(self, player):
        if self.pure_product_space is None:
            self.players.append(player)
            self.players_num += 1
        else:
            print("ERORR: cannot join new players any more")
            sys.exit(1)

    def player_assign_random_payoff(self):
        self.build_product_space_of_pures()
        for player in self.players:
            player.assign_random_payoff(len(self.pure_product_space))
        print("Payoff functions were randomized")

    def player_assign_payoff(self, player_index, strategies_str, payoff):
        self.build_product_space_of_pures()
        # player index starts from 0, and hence minus 1
        the_player = self.players[player_index - 1]
        # this will be a terrible searching
        for i, combi in enumerate(self.pure_product_space):
            # strategy index starts from 1, and hence add 1
            strategies_str_2 = "".join(str(x + 1) for x in combi)
            if strategies_str == strategies_str_2:
                the_player.assign_payoff(len(self.pure_product_space), i, payoff)
                break

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
                    "Error: %s players %s initial strategies"
                    % (self.players_num, len(init_strategies))
                )
                sys.exit(1)
            for i, player in enumerate(self.players):
                if len(init_strategies[i]) == player.pure_strategies_num:
                    player.mixed_strategy = np.array(init_strategies[i])
                else:
                    print(
                        "Error: player %s with %s pures initialized to %s"
                        % (i + 1, player.pure_strategies_num, init_strategies[i])
                    )
                    sys.exit(1)
            print("Initial strategies were customized")

    def build_product_space_of_pures(self):
        if self.pure_product_space is not None:
            # product space was built
            return
        temp_l = []
        for player in self.players:
            temp_l.append(set(range(player.pure_strategies_num)))
        self.pure_product_space = list(itertools.product(*temp_l))

    def compute_joint_dist_on_vertex(self, player_index, pure_strategy_index):
        """
        return the prob dist computed when the player changes its to the one
        specified in the parameter `pure_strategy_index` in the meantime the other
        players keep theirs unchanged.
        index i: for player
        index j: for pure strategies of player i
        index k: for the combination of pure strategies in `pure_product_space` and `prob_dict`
        time complexity: (n-1)g^(n-1) multiplications
        """
        prob_dist = np.zeros(len(self.pure_product_space))
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

    def eqpt(self):
        eqpts = [p.mixed_strategy for p in self.players]
        regret_sum = [p.regret_vector for p in self.players]
        return eqpts, regret_sum

    def regret_sum_aggregation(self):
        return np.sum([p.regret_vector.sum() for p in self.players])

    def show_eqpt(self, eqpt):
        regret_sum_l = []
        print("================== Nash Equilibrium Approximation ==================")
        for i, (mixed, vgv) in enumerate(zip(eqpt[0], eqpt[1])):
            regret_sum_l.append(vgv.sum())
            print(
                "Player %s:" % (i + 1),
                "Nash Eq.",
                mixed.round(4).tolist(),
                "Deviation",
                vgv.round(4).tolist(),
            )
        regret_sum_a = np.array(regret_sum_l).round(4)
        print(
            "Deviation Sum:",
            *regret_sum_a,
            "Overall Deviation Sum: %s" % np.round(regret_sum_a.sum(), 4)
        )

    def player_run_one_iteration(self, rate):
        """time complexity: n(n-1)g^n multiplications
        multiprocessing would be nice here, supposedly reducing O(n^2g^n) to O(ng^n)
        """

        for i, player in enumerate(self.players):
            player.run_one_iteration(self, rate, i)

    def plot_2(self):
        # if any player is not using two pure strategies, quit plotting
        for aplayer in self.players:
            if np.array(aplayer.path_l).shape[1] != 2:
                print("ERROR: at least one player is not using TWO pure strategies")
                sys.exit(1)

        try:
            import matplotlib.pyplot as plt
        except:
            print("ERROR: you haven't installed matplotlib packages")
            sys.exit(1)

        plt.figure(figsize=(16, 8))
        ax = plt.gca()

        for aplayer in self.players:
            xy = np.array(aplayer.path_l)
            ax.plot(xy[:, 0], alpha=1, zorder=2)

        plt.tight_layout()
        self.get_random_file_name()
        plt.savefig(self.plot_file_name, bbox_inches="tight", dpi=self.fig_dpi)
        plt.show()

    def barycentric_to_cartesian(self, strategy_a):
        barycentric_x = np.array([0, np.sqrt(2) / 2, np.sqrt(2)]).T
        barycentric_y = np.array([0, np.sqrt(6) / 2, 0]).T
        return strategy_a.dot(barycentric_x), strategy_a.dot(barycentric_y)

    def plot_3(self):
        # if any player uses less than three pure strategies, quit plotting
        for aplayer in self.players:
            if np.array(aplayer.path_l).shape[1] != 3:
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

        for aplayer in self.players:
            x_a, y_a = self.barycentric_to_cartesian(np.array(aplayer.path_l))
            ax.plot(x_a, y_a, alpha=0.5, zorder=2)

        plt.tight_layout()
        self.get_random_file_name()
        plt.savefig(self.plot_file_name, bbox_inches="tight", dpi=self.fig_dpi)
        plt.show()

    def get_random_file_name(self):
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
        regret_sum_ag_old = 10**10  # super big number to start with
        for _ in range(iterations):
            self.player_run_one_iteration(rate)
            regret_sum_ag_cur = self.regret_sum_aggregation()
            if regret_sum_ag_cur < regret_sum_ag_old:
                eqpt = self.eqpt()
                regret_sum_ag_old = regret_sum_ag_cur

        self.show_eqpt(eqpt)


if __name__ == "__main__":
    pass
