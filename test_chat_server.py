import chat_server
import socket
import mock


def test_broadcast(mocker):
	
	#mocker.patch('chat_server.remove_username', return_value=None)
	client = mock.Mock()
	client.send.return_value = None
	client1 = mock.Mock()

	#mocker.patch('socket.socket', return_value=client)
	with mocker.patch('chat_server.clients', new_callable=PropertyMock) as mock_clients:
		mock_clients.return_value = [client,client]
		spy = mocker.spy(chat_server, 'broadcast')
		assert chat_server.clients.count() == 2

		spy = mocker.spy(chat_server, 'remove')
		assert chat_server.clients.count() == 1

		assert chat_server.broadcast('hola', client1) == None
		assert spy.call_count == 1
		assert spy.spy_return == None



#def test_filter_address():
#	assert chat_server.filter_address(psutil.net_if_addrs().items()) == False
	

