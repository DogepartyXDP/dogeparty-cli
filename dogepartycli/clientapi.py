import sys
import logging
import binascii
from urllib.parse import quote_plus as urlencode

from dogepartylib.lib import config, script
from dogepartycli import util
from dogepartycli import wallet
from dogepartycli import messages
from dogepartycli.messages import get_pubkeys

logger = logging.getLogger()

DEFAULT_REQUESTS_TIMEOUT = 5 # seconds

class ConfigurationError(Exception):
    pass

def initialize(testnet=False, testcoin=False, regtest=True, customnet="",
                dogeparty_rpc_connect=None, dogeparty_rpc_port=None,
                dogeparty_rpc_user=None, dogeparty_rpc_password=None,
                dogeparty_rpc_ssl=False, dogeparty_rpc_ssl_verify=False,
                wallet_name=None, wallet_connect=None, wallet_port=None,
                wallet_user=None, wallet_password=None,
                wallet_ssl=False, wallet_ssl_verify=False,
                requests_timeout=DEFAULT_REQUESTS_TIMEOUT):

    def handle_exception(exc_type, exc_value, exc_traceback):
        logger.error("Unhandled Exception", exc_info=(exc_type, exc_value, exc_traceback))
    sys.excepthook = handle_exception

    # testnet
    config.TESTNET = testnet or False

    config.REGTEST = regtest or False

    if len(customnet) > 0:
        config.CUSTOMNET = True
        config.REGTEST = True
    else:
        config.CUSTOMNET = False

    # testcoin
    config.TESTCOIN = testcoin or False

    ##############
    # THINGS WE CONNECT TO

    # Server host (Dogecoin Core)
    config.DOGEPARTY_RPC_CONNECT = dogeparty_rpc_connect or 'localhost'

    # Server RPC port (Dogecoin Core)
    if dogeparty_rpc_port:
        config.DOGEPARTY_RPC_PORT = dogeparty_rpc_port
    else:
        if config.TESTNET:
            config.DOGEPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_TESTNET
        elif config.CUSTOMNET:
            config.DOGEPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_REGTEST
        elif config.REGTEST:
            config.DOGEPARTY_RPC_PORT = config.DEFAULT_RPC_PORT_REGTEST
        else:
            config.DOGEPARTY_RPC_PORT = config.DEFAULT_RPC_PORT
    try:
        config.DOGEPARTY_RPC_PORT = int(config.DOGEPARTY_RPC_PORT)
        if not (int(config.DOGEPARTY_RPC_PORT) > 1 and int(config.DOGEPARTY_RPC_PORT) < 65535):
            raise ConfigurationError('invalid RPC port number')
    except:
        raise Exception("Please specific a valid port number dogeparty-rpc-port configuration parameter")

    # Server RPC user (Dogecoin Core)
    config.DOGEPARTY_RPC_USER = dogeparty_rpc_user or 'rpc'

    # Server RPC password (Dogecoin Core)
    if dogeparty_rpc_password:
        config.DOGEPARTY_RPC_PASSWORD = dogeparty_rpc_password
    else:
        config.DOGEPARTY_RPC_PASSWORD = None

    # Server RPC SSL
    config.DOGEPARTY_RPC_SSL = dogeparty_rpc_ssl or False  # Default to off.

    # Server RPC SSL Verify
    config.DOGEPARTY_RPC_SSL_VERIFY = dogeparty_rpc_ssl_verify or False # Default to off (support self‐signed certificates)

    # Construct server URL.
    config.DOGEPARTY_RPC = config.DOGEPARTY_RPC_CONNECT + ':' + str(config.DOGEPARTY_RPC_PORT)
    if config.DOGEPARTY_RPC_PASSWORD:
        config.DOGEPARTY_RPC = urlencode(config.DOGEPARTY_RPC_USER) + ':' + urlencode(config.DOGEPARTY_RPC_PASSWORD) + '@' + config.DOGEPARTY_RPC
    if config.DOGEPARTY_RPC_SSL:
        config.DOGEPARTY_RPC = 'https://' + config.DOGEPARTY_RPC
    else:
        config.DOGEPARTY_RPC = 'http://' + config.DOGEPARTY_RPC
    config.DOGEPARTY_RPC += '/rpc/'

    # DOGE Wallet name
    config.WALLET_NAME = wallet_name or 'dogecoincore'

    # DOGE Wallet host
    config.WALLET_CONNECT = wallet_connect or 'localhost'

    # DOGE Wallet port
    if wallet_port:
        config.WALLET_PORT = wallet_port
    else:
        if config.TESTNET:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_TESTNET
        elif config.CUSTOMNET:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_REGTEST
        elif config.REGTEST:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT_REGTEST
        else:
            config.WALLET_PORT = config.DEFAULT_BACKEND_PORT
    try:
        config.WALLET_PORT = int(config.WALLET_PORT)
        if not (int(config.WALLET_PORT) > 1 and int(config.WALLET_PORT) < 65535):
            raise ConfigurationError('invalid wallet API port number')
    except:
        raise ConfigurationError("Please specific a valid port number wallet-port configuration parameter")

    # DOGE Wallet user
    config.WALLET_USER = wallet_user or 'dogecoinrpc'

    # DOGE Wallet password
    if wallet_password:
        config.WALLET_PASSWORD = wallet_password
    else:
        raise ConfigurationError('wallet RPC password not set. (Use configuration file or --wallet-password=PASSWORD)')

    # DOGE Wallet SSL
    config.WALLET_SSL = wallet_ssl or False  # Default to off.

    # DOGE Wallet SSL Verify
    config.WALLET_SSL_VERIFY = wallet_ssl_verify or False # Default to off (support self‐signed certificates)

    # Construct DOGE wallet URL.
    config.WALLET_URL = urlencode(config.WALLET_USER) + ':' + urlencode(config.WALLET_PASSWORD) + '@' + config.WALLET_CONNECT + ':' + str(config.WALLET_PORT)
    if config.WALLET_SSL:
        config.WALLET_URL = 'https://' + config.WALLET_URL
    else:
        config.WALLET_URL = 'http://' + config.WALLET_URL

    config.REQUESTS_TIMEOUT = requests_timeout

    # Encoding
    if config.TESTCOIN:
        config.PREFIX = b'XX'                   # 2 bytes (possibly accidentally created)
    else:
        #config.PREFIX = b'CNTRPRTY'             # 8 bytes
        config.PREFIX = b'DOGEPRTY'             # 8 bytes

    # (more) Testnet
    if config.TESTNET:
        config.MAGIC_BYTES = config.MAGIC_BYTES_TESTNET
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_TESTNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_TESTNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_TESTNET_TESTCOIN
            config.BURN_START = config.BURN_START_TESTNET_TESTCOIN
            config.BURN_END = config.BURN_END_TESTNET_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_TESTNET
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_TESTNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_TESTNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_TESTNET
            config.BURN_START = config.BURN_START_TESTNET
            config.BURN_END = config.BURN_END_TESTNET
            config.UNSPENDABLE = config.UNSPENDABLE_TESTNET
    elif config.CUSTOMNET:
        custom_args = customnet.split('|')

        if len(custom_args) == 3:
            config.MAGIC_BYTES = config.MAGIC_BYTES_REGTEST
            config.ADDRESSVERSION = binascii.unhexlify(custom_args[1])
            config.P2SH_ADDRESSVERSION = binascii.unhexlify(custom_args[2])
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST
            config.BURN_START = config.BURN_START_REGTEST
            config.BURN_END = config.BURN_END_REGTEST
            config.UNSPENDABLE = custom_args[0]
        else:
            raise "Custom net parameter needs to be like UNSPENDABLE_ADDRESS|ADDRESSVERSION|P2SH_ADDRESSVERSION (version bytes in HH format)"
    elif config.REGTEST:
        config.MAGIC_BYTES = config.MAGIC_BYTES_REGTEST
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_REGTEST
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_REGTEST
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST_TESTCOIN
            config.BURN_START = config.BURN_START_REGTEST_TESTCOIN
            config.BURN_END = config.BURN_END_REGTEST_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_REGTEST
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_REGTEST
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_REGTEST
            config.BLOCK_FIRST = config.BLOCK_FIRST_REGTEST
            config.BURN_START = config.BURN_START_REGTEST
            config.BURN_END = config.BURN_END_REGTEST
            config.UNSPENDABLE = config.UNSPENDABLE_REGTEST
    else:
        config.MAGIC_BYTES = config.MAGIC_BYTES_MAINNET
        if config.TESTCOIN:
            config.ADDRESSVERSION = config.ADDRESSVERSION_MAINNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_MAINNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_MAINNET_TESTCOIN
            config.BURN_START = config.BURN_START_MAINNET_TESTCOIN
            config.BURN_END = config.BURN_END_MAINNET_TESTCOIN
            config.UNSPENDABLE = config.UNSPENDABLE_MAINNET
        else:
            config.ADDRESSVERSION = config.ADDRESSVERSION_MAINNET
            config.P2SH_ADDRESSVERSION = config.P2SH_ADDRESSVERSION_MAINNET
            config.BLOCK_FIRST = config.BLOCK_FIRST_MAINNET
            config.BURN_START = config.BURN_START_MAINNET
            config.BURN_END = config.BURN_END_MAINNET
            config.UNSPENDABLE = config.UNSPENDABLE_MAINNET

WALLET_METHODS = [
    'get_wallet_addresses', 'get_doge_balances', 'sign_raw_transaction',
    'get_pubkey', 'is_valid', 'is_mine', 'get_doge_balance', 'send_raw_transaction',
    'wallet', 'asset', 'balances', 'pending', 'is_locked', 'unlock', 'wallet_last_block',
    'sweep'
]

def call(method, args, pubkey_resolver=None):
    """
        Unified function to call Wallet and Server API methods
        Should be used by applications like `dogeparty-gui`

        :Example:

        import dogepartycli.clientapi
        clientapi.initialize(...)
        unsigned_hex = clientapi.call('create_send', {...})
        signed_hex =  clientapi.call('sign_raw_transaction', unsigned_hex)
        tx_hash = clientapi.call('send_raw_transaction', signed_hex)
    """
    if method in WALLET_METHODS:
        func = getattr(wallet, method)
        return func(**args)
    else:
        if method.startswith('create_'):
            # Get provided pubkeys from params.
            pubkeys = []
            for address_name in ['source', 'destination']:
                if address_name in args:
                    address = args[address_name]
                    if script.is_multisig(address) or address_name != 'destination':    # We don’t need the pubkey for a mono‐sig destination.
                        pubkeys += get_pubkeys(address, pubkey_resolver=pubkey_resolver)
            args['pubkey'] = pubkeys

        result = util.api(method, args)

        if method.startswith('create_'):
            messages.check_transaction(method, args, result)

        return result


# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
