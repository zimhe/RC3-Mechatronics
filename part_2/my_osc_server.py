
from pythonosc import dispatcher
from pythonosc import osc_server

address=("0.0.0.0",8080)

dispatcher=dispatcher.Dispatcher()

def dispatch_callback(pattern,function):
    dispatcher.map(pattern,function)


def server_threading(args,_dispatcher):
    server=osc_server.ThreadingOSCUDPServer((args[0],args[1]),_dispatcher)
    print("servering on {}".format(server.server_address))
    server.serve_forever()
