from lib2to3.pgen2 import token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .nft_util import get_my_token

@api_view(['GET'])
def my_token(request):
    address = request.GET.get('address','')
    print(request.GET)
    token_info = get_my_token(address)
    return Response(token_info)
    