from typing import Text, Dict
import os

from .EUSignCP_20200521.Interface.EUSignCP import *


def verify_internal(data_path: os.PathLike) -> [Dict, None]:
    EULoad()
    pIface = EUGetInterface()
    try:
        pIface.Initialize()
    except Exception as e:
        print("Initialize failed" + str(e))
        EUUnload()
        return
    try:
        data = open(data_path, 'rb').read()
        d = []
        S = {}
        pIface.VerifyDataInternal(None, data, len(data), d, S)
        return {'data': d[0], 'cert': S}
    except Exception as e:
        pIface.Finalize()
        EUUnload()
    finally:
        pIface.Finalize()
        EUUnload()


def verify_external(data_path: os.PathLike, sign_path: [None, os.PathLike] = None,
                    sign_data: [Text, None] = None) -> Dict:
    try:
        print("load library")
        EULoad()
        print("EUGetInterface")
        pIface = EUGetInterface()
        print("Initialize")
        pIface.Initialize()
    except Exception as e:
        print("Initialize failed" + str(e))
        ##EUUnload()
        return {'code_message': str(e), 'code': 2}
    try:
        data = open(data_path, 'rb').read()
        S = {}
        if sign_path:
            sign = open(sign_path, 'rb').read()
            pIface.VerifyData(data, len(data), None, sign, len(sign), S)
        elif sign_data:
            sign_64 = sign_data
            print('VerifyData')
            pIface.VerifyData(data, len(data), sign_64, None, len(sign_64), S)
            ##pIface.VerifyData(pData, len(pData), None, lSign[0], len(lSign[0]), None)
        return {'cert': S, 'code': 0, 'code_message': 'Успішно'}
    except Exception as e:
        print(e)
        pIface.Finalize()
        ##EUUnload()
        return {'code_message': str(e), 'code': 1}
    finally:
        pIface.Finalize()
        ##EUUnload()


def get_signer_info(sign_data: Text) -> Dict:
    try:
        print("load library")
        EULoad()
        print("EUGetInterface")
        pIface = EUGetInterface()
        print("Initialize")
        pIface.Initialize()
    except Exception as e:
        print("Initialize failed" + str(e))
        return {'code_message': str(e), 'code': 2}

    try:
        print('GetSignerInfo')
        S = {}
        d = []
        pIface.GetSignerInfo(0, sign_data, None, len(sign_data), S, d)
        return {'cert_info': S, 'code': 0, 'code_message': 'Успішно', "cert_data": d[0]}
    except Exception as e:
        print(e)
        pIface.Finalize()
        return {'code_message': str(e), 'code': 1}
    finally:
        pIface.Finalize()
