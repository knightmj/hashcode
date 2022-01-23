import os.path
import random
import sys
import time


class PizzaParty:
    def __init__(self, toppings):
        self.toppings = set(toppings)
        self.clients = []

    def add_client(self, client):
        self.clients.append(client)

    def combine(self, other_party, all_clients):
        party = PizzaParty(self.toppings | other_party.toppings)
        self.filter_clients(all_clients, party)
        return party

    def remove_topping(self, topping, all_clients):
        toppings = set(self.toppings)
        toppings.remove(topping)
        party = PizzaParty(toppings)
        self.filter_clients(all_clients, party)
        return party

    def members(self):
        return len(self.clients)

    @staticmethod
    def filter_clients(all_clients, party):
        for client in all_clients:
            # does this client dislike this pizza?
            if client.will_buy(party.toppings):
                party.clients.append(client)

    def __lt__(self, other):
        # secondary sort by least dislikes
        return len(self.clients) > len(other.clients)


class Solver:
    def solve(self, clients):
        pass


class TakeAway(Solver):

    def solve(self, clients):
        toppings = set()
        for client in clients:
            toppings |= client.likes
        party = PizzaParty(toppings)
        PizzaParty.filter_clients(clients, party)
        best = PizzaParty(set(party.toppings))
        PizzaParty.filter_clients(clients, best)
        most = best.members()
        while len(party.toppings) > 0:
            better = set()
            # print(len(party.toppings), best.members(), len(best.toppings), flush=True)
            toppings = list(party.toppings)
            for topping in toppings:
                new_party = party.remove_topping(topping, clients)
                if new_party.members() > party.members():
                    better.add(topping)
                if new_party.members() > most:
                    best = new_party
                    most = new_party.members()
            if len(better) > 0:
                party = PizzaParty(party.toppings - better)
                PizzaParty.filter_clients(clients, party)
            else:
                return best.toppings

        return best.toppings


class RandomWalk(Solver):
    def __init__(self):
        self.parties = []

    def solve(self, clients, top_options=50):
        # make a pizza party for every client
        # topping with at least what they lke
        perfect_pizza = {}
        for client in clients:
            key = str(client.likes)
            if key not in perfect_pizza:
                perfect_pizza[key] = PizzaParty(client.likes)

            perfect_pizza[key].add_client(client)

        cur_parties = [perfect_pizza[k] for k in perfect_pizza]
        most = 0
        max_party = None
        for party in cur_parties:
            if len(party.clients) > most:
                most = len(party.clients)
                max_party = party

        self.parties = random.sample(cur_parties, min(len(cur_parties), top_options))
        while len(cur_parties) > 0:
            cur_parties.sort()
            # only keep the top
            cur_parties = random.sample(cur_parties, min(len(cur_parties), top_options))
            new_parties = []
            for party_a in cur_parties:
                for party_b in self.parties:
                    if party_a == party_b:
                        continue
                    combined = party_a.combine(party_b, clients)
                    new_size = len(combined.clients)

                    if (new_size > len(party_a.clients) and
                            new_size > len(party_b.clients)):
                        # this is better than the children and better than we have seen
                        new_parties.append(combined)
                    if new_size > most:
                        most = len(combined.clients)
                        max_party = combined

            if cur_parties != self.parties:
                self.parties += cur_parties
                # only keep some randomly
                self.parties = random.sample(cur_parties, min(len(cur_parties), top_options))
            cur_parties = new_parties
        return max_party.toppings


class Client:
    id_offset = 0

    def __init__(self, l1, l2):
        self.id = Client.id_offset
        Client.id_offset += 1
        self.likes = set(l1.split()[1:])
        self.dislikes = set(l2.split()[1:])

    def __str__(self):
        return str(self.id) + " l:" + " ".join(sorted(list(self.likes))) + \
               " d:" + " ".join(sorted(list(self.dislikes)))

    def will_buy(self, toppings):
        return len(toppings.intersection(self.likes)) == len(self.likes) and \
               len(toppings.intersection(self.dislikes)) == 0

    @staticmethod
    def load(file):
        with open(file) as f:
            lines = f.readlines()
        clients = []
        for i in range(1, len(lines), 2):
            clients.append(Client(lines[i], lines[i + 1]))
        return clients

    @staticmethod
    def buyers(toppings, clients):
        buyers = 0
        for client in clients:
            if client.will_buy(toppings):
                buyers += 1
        return buyers


def get_dataset_path(dataset):
    dataset_dir = os.path.dirname(__file__)
    files = {'a': 'a_an_example.in.txt',
             'b': 'b_basic.in.txt',
             'c': 'c_coarse.in.txt',
             'd': 'd_difficult.in.txt',
             'e': 'e_elaborate.in.txt'}
    file = os.path.join(dataset_dir, os.path.join('input_data'))
    if dataset in files:
        file = os.path.join(file, files[dataset])
    else:
        raise "Invalid dataset: " + dataset
    return file


def load_dataset(dataset):
    file = get_dataset_path(dataset)
    return Client.load(file)


def test_answer():
    return set(['cheese', 'mushrooms', 'tomatoes', 'peppers'])


def one_pizza(datasets):
    total = 0
    for dataset in datasets:
        clients = load_dataset(dataset)

        toppings = TakeAway().solve(clients)
        points = Client.buyers(toppings, clients)
        print("dataset", dataset, "TakeAway found:",
              points, flush=True)
        name = dataset + "_" + str(points)
        if not os.path.exists(name):
            print("saving", name)
            with(open(name, "w")) as f:
                f.write(str(len(toppings)) + " " + " ".join(sorted(list(toppings))))

        total += points
    print("Total points:", total)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("run python one_pizza.py [dataset] where dataset is one oe more is a,b,c,d or e")
    one_pizza(sys.argv[1])
