from mock import Mock

from game import *

def test_game():
    Game.getConfig = Mock()
    game = Game()
    print game.getConfig()
    assert False