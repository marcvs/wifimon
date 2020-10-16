#!/usr/bin/env python3
'''main entry point'''

#vim: foldmethod=indent
# vim: tw=100 foldmethod=marker
#
# This code is distributed under the MIT License
#
# pylint: disable=invalid-name, superfluous-parens
# pylint: disable=logging-not-lazy, logging-format-interpolation

import logging
from wifitop.parse_args import args

logger = logging.getLogger(__name__)

def main():
    '''Main Config'''
    try: # initialize threads

        # initialize queues
        # client_q   = queue.Queue()
        # response_q = queue.Queue()

        # # initialize clientAnalysisThread
        # clientAnalysis = ClientAnalysisThread(client_q, response_q, args, ethers)
        # clientAnalysis.setDaemon(True)
        # clientAnalysis.start()

        # start the app
        # app.run(debug=True, host='0.0.0.0', port=int(args.port))
        print ("hello")
    except Exception as e:
        # We can also close the cursor if we are done with it
        logging.error("error on thread startup: " + str(e))
        raise(e)
    return (0)

if __name__ == '__main__':
    # Run the app
    main()

