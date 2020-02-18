# 단일 스레드에서 비동기적으로 처리
# DB query 요청이나 네트워크 요청, 파일 IO 등의 작업은 CPU를 거의 사용하지 않음.
import asyncio
from urllib.request import urlopen
import time

async def get_url_data(url:str) -> (str, str, str):
  '''특정 URL에 요청을 보내어 HTML 문서를 문자열로 받는다.
  url, 응답텍스트, 포맷팅된 소요시간을 리턴한다.'''
  print(f'Request for: {url}')
  s = time.time()
  res = urlopen(url)
  data = res.read().decode()
  return url, data, f'{time.time() -  s: .3f}'


async def get_url_data2(url):
  print(f'Request for: {url}')
  loop = asyncio.get_event_loop()
  s = time.time()
  # 기존의 표준 함수들도 병렬적으로 동작하는 코루틴으로 전환할 수 있음.
  # await : 코루틴 내에서 다른 코루틴을 호출하고 그 결과를 받을 때 사용. 다른 비동기 코루틴을 호줄하되, 해당 작업이 완료될 때까지 기다린다는 뜻.
  res = await loop.run_in_executor(None, urlopen, url)
  data = res.read().decode()
  return url, data, f'{time.time() -  s: .3f}'

urls = (
  'https://www.naver.com',
  'https://www.daum.net',
  'https://www.yahoo.com',
  'http://fa.bianp.net/',
  'https://jakevdp.github.io',
  'http://arogozhnikov.github.io'
)


# 다만, 이는 스레드를 별도로 생성해서 동작하기 때문에 메모리 자원을 보다 많이 사용하게 되는 문제가 있고, 또한 I/O 바운드되는 작업에만 적용할 수 있다.
async def test_urls(co, urls):
  s = time.time()
  fs = {co(url) for url in urls}
  for f in asyncio.as_completed(fs):
    url, body, t = await f
    print(f'Resonse from: {url}, {len(body)}Bytes - {f}sec')
  print(f'{time.time() - s:0.3f}sec')

loop = asyncio.get_event_loop()
loop.run_until_complete(test_urls(get_url_data, urls))

loop = asyncio.get_event_loop()
loop.run_until_complete(test_urls(get_url_data2, urls))