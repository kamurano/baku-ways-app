from typing import Annotated

from fastapi.responses import JSONResponse
import httpx
from fastapi import APIRouter, Query
from wireup import Inject

from app.core.container import container
from app.schemas.transit import TransitModel
from configs.settings import Settings


router = APIRouter(prefix="/transit", tags=["transit"])


@router.get("/")
@container.autowire
async def get_transit_routes(
    origin_lat: Annotated[float, Query(description="Origin latitude")],
    origin_lng: Annotated[float, Query(description="Origin longitude")],
    destination_lat: Annotated[float, Query(description="Destination latitude")],
    destination_lng: Annotated[float, Query(description="Destination longitude")],
    settings: Annotated[Settings, Inject()]
):
    url = settings.GOOGLE_MAPS_TRANSIT_API_URL
    params = {
        "origin": f"{origin_lat},{origin_lng}",
        "destination": f"{destination_lat},{destination_lng}",
        "mode": "transit",
        "alternatives": True,
        "transit_mode": "train|subway",
        "key": settings.GOOGLE_MAPS_API_KEY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        data = response.json()

        print(data)

        if response.status_code == 200 and data["status"] == "OK":
            try:
                data = TransitModel.model_validate(data)
                print(data)
                return data
            except Exception as e:
                return JSONResponse(data)
        else:
            return JSONResponse(status_code=400, content={"message": "Error fetching transit data"})



@router.get("/fast-transit")
async def javid_going_home():
    return [
        {
            "type": "subway",
            "duration": "24m",
            "polyline": "evmuF}bgoHaB_@qCq@}@Sg@Ie@Ee@?exAlGyABuAAoAMiAWkAc@y@]y@a@m@_@m@c@e@m@_@q@[y@c@}AgAkEgAkEQ_AMw@I}@GkAEsAm@oT{BkbAEs@Iq@Kk@Mg@Qg@uAyDwAwDaMu]oAcDqAaDyAgDyAsCcB{CeBqCuAcBqAwAaBmAcBaAqLuHcAcA_AoA{@cB}@oBw@mBq@qBg@sBa@uBg@iEc@uEa@qEa@qEwBoVoEkh@_B_SOuBSuBUuBYuBYqB_@qBa@mBg@mBk@kBcB{EiFmN[_ASaAOy@K_AEaACq@?o@@u@B}@Bc@Dc@P{BP{BFy@lCo\\VoCVmCdHym@l@iFl@gFlAoK\\uCFa@J]NUTUx]aVnCkBnCkBlRkMvOcKlXwP|J_HvCoBtCoBnDaCPKRIRETCZA`@AzBG|@A|@?vFAf_@EnHAbDA"
        },
        {
            "type": "bus",
            "duration": "8m",
            "polyline": "ixnuFmt{oH?h@{CEU?_@?o@?A?cCEMCA\\?T@LBXf@\\HDJDH@bBAB?vA?vA?pB?B?t@?|B?h@?dA?^?R?dA?@?`@C^GTITMJGFCNMJMHQFIdDE`EAX?LAr@Bb@H^Nh@\\DJFJFHFHHDJDHBJ@B?@?B?B?B?B?B?B?FAFAFAFADCFCFEDCDEDGBEDGBGBI@GBI@E?E@E?G?E?E?E?G?E?E?GAE?EAEAECEj@iARYX]FGRUBCBCTU~@_ARSFIZ[RSHIl@m@HIZ]`DcDv@u@BEDElBiBb@_@l@c@zCaBx@]pAe@~@YZKPEt@WZKr@M\\CF?pAEZAlAA\\?D?D?D?D?B?@?D?D?D?D?D?D?D?D?D?D?D?D?DAD?D?D?D?D?D?B?D?@?B?D?D?D?D?@?B?DAD?D?D?DAD?D?D?D?DAD?B?@?D?D?BA@?D?D?@?B?DAD?D?D?D?BA@?D?D?B?@?D?DA@?@?@?D?D?DAD?D?B?D?DAD?D?D?D?BAP?`@Eb@?b@Ab@?jBCfAArACLAL?`GMJAtB@x@?z@\\x@\\j@WH]Po@zDe@BP"
        }
    ]

@router.get("/fast-trasit-request")
async def javid_going_home_pro():
    data = []
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://maps.googleapis.com/maps/api/directions/json?origin=40.37935571457436,49.84843148916777&destination=40.38515013007684,49.95444123741532&{Settings.GOOGLE_MAPS_API_KEY}=AIzaSyCUBH27B1wRp2c1sTZq_MY-mqRzJLtMqJc&mode=transit")
        
        data.append(response.json())
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://maps.googleapis.com/maps/api/directions/json?origin=40.38515013007684,49.95444123741532&destination=40.3642892270327,49.960384479276215&{Settings.GOOGLE_MAPS_API_KEY}=AIzaSyCUBH27B1wRp2c1sTZq_MY-mqRzJLtMqJc&mode=transit")
        
        data.append(response.json())

    return data
