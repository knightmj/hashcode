import os.path
import sys


class Client:
    id_offset = 0

    def __init__(self, l1, l2):
        self.id = Client.id_offset + 1
        Client.id_offset +=  1
        self.likes = set(l1.split()[1:])
        self.dislikes = set(l2.split()[1:])

    def __str__(self):
        return str(self.id) + " l:" + " ".join(self.likes) + " d:" + " ".join(self.dislikes)

    def will_buy(self, toppings):
        return len(toppings.intersection(self.likes)) == len(self.likes) and \
               len(toppings.intersection(self.dislikes)) == 0

    @staticmethod
    def load(file):
        with open(file) as f:
            lines = f.readlines()
        clients = []
        for i in range(1, len(lines), 2):
            clients.append(Client(lines[i], lines[i+1]))
        return clients

    @staticmethod
    def buyers(toppings, clients):
        buyers = 0
        for client in clients:
            if client.will_buy(toppings):
                buyers += 1
        return buyers


def get_dataset_path(dataset):
    dir = os.path.dirname(__file__)
    files = {'a': 'a_an_example.in.txt',
             'b': 'b_basic.in.txt',
             'c': 'c_coarse.in.txt',
             'd': 'd_difficult.in.txt',
             'e': 'e_elaborate.in.txt'}
    file = os.path.join(dir, os.path.join('input_data'))
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
    for dataset in datasets:
        clients = load_dataset(dataset)
        print("Clients:", len(clients))
        toppings = test_answer()
        print("buyers:", Client.buyers(toppings, clients), "of", " ".join(toppings))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("run python one_pizza.py [dataset] where dataset is one oe more is a,b,c,d or e")
    one_pizza(sys.argv[1])
