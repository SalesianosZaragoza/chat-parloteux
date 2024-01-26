import chat_server
import socket
# pip install pytest-mock pytest

def test_broadcastClientSendCalled(mocker):
	
	#mocker.patch('chat_server.remove_username', return_value=None)
	client = mocker.Mock()
	client.send.return_value = None
	
	spy = mocker.spy(chat_server, 'remove')
	chat_server.clients = [client,client]
	assert len(chat_server.clients) == 2

	mocker.patch('chat_server.remove_username', return_value=None)


	assert chat_server.broadcast('hola', None) == None
	assert client.send.called
	assert spy.call_count == 0

def test_broadcastClientSendNotCalled(mocker):
	
	#mocker.patch('chat_server.remove_username', return_value=None)
	client = mocker.Mock()
	client.send.return_value = None
	
	chat_server.clients = [client,client]
	assert len(chat_server.clients) == 2

	mocker.patch('chat_server.remove_username', return_value=None)
	spy = mocker.spy(chat_server, 'remove')


	assert chat_server.broadcast('hola', client) == None
	assert not client.send.called
	
def test_broadcastClientSendException(mocker):
	
	#mocker.patch('chat_server.remove_username', return_value=None)
	client = mocker.Mock()
	client.send.side_effect = socket.error()
	
	chat_server.clients = [client,client]
	assert len(chat_server.clients) == 2
	mocker.patch('chat_server.remove_username', return_value=None)
	spy = mocker.spy(chat_server, 'remove')


	assert chat_server.broadcast('hola', None) == None
	assert client.send.called
	assert spy.called == True
	




#def test_filter_address():
#	assert chat_server.filter_address(psutil.net_if_addrs().items()) == False
	

