from gws.window import BasicWindow
from gws._errors import FailedNetworkRequest
import requests
import webbrowser

class RobloxWindow(BasicWindow):
    def list_servers(self, place_id: int, limit: int = 25, pages: int = 1) -> list[dict]:
        '''Calls the roblox API to list availible servers for a game. This returns limit servers per page, and can request as many pages as there are availbile on the API. Stops automatically if there
        are no more pages to look at

        NOTE: It's not really recommended to get too many pages, or send too many requests in general, as you can get rate limited quite fast
        
        For reference, the endpoint called is: https://games.roblox.com/v1/games/[game id]/servers/[text that doesn't seem to mattter, maybe it's a server ID? Not sure, but it's just 'game' here]
        
        :param int place_id: The ID of the place (or game) to list servers for
        :param int limit: How many servers to return, according to roblox: "Can only be 10, 25, 50, or 100"
        :param int pages: How many pages of limit servers to return'''
        # requesting it all the pages
        servers: list[dict] = []
        next_page_cursor: str | None = None

        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "DNT": "1",
            "Host": "games.roblox.com",
            "Pragma": "no-cache",
            "Priority": "u=0, i",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-GPC": "1",
            "TE": "trailers",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:147.0) Gecko/20100101 Firefox/147.0"
        }

        cookies = {
            'GuestData': 'UserID=-121495612'
        }


        
        for i in range(pages):
            # constructing the full url to request
            request_location = f'https://games.roblox.com/v1/games/{place_id}/servers/0?limit={limit}'

            # requesting it
            response = requests.get(request_location, headers=headers, params={'limit': limit, 'cursor': next_page_cursor}, cookies=cookies)

            # if it's not an ok status code, raising an error
            if not response.ok:
                raise FailedNetworkRequest(f'Got status code {response.status_code} when requesting {request_location} to get availble servers for a game. The returned data was: {response.content.decode()}')

            # adding it's response data to our list of data
            servers += response.json().get('data')

            # setting the next page cursor to the next page cursor
            next_page_cursor = response.json().get('nextPageCursor')

            # if there is no next_page_cursor (that means we went through all servers)
            # we break out of the loop
            if next_page_cursor is None:
                break
        
        # returning the response(s)
        return servers

    def open(self, place_id: int | None = None, game_instance_id: str | None = None):
        '''Opens Roblox using it's URL (URI?) scheme roblox://

        roblox:// should work for most non-official roblox clients, but if it doesn't
        you can change it by changing the url_scheme parameter to something besides
        roblox://

        The way this works is by checking parameter A, let's say place_id. Is it None?
        If yes: go on to the next parameter and check that
        
        If no: join the game/place, then also pass the other info

        The reason it's done like this is because if you wanted to open to a chat with
        somebody, you'd do roblox://navigation/chat?userId='the user id',
        but if you wanted to view someone's posts, you'd do
        roblox://navigation/content_posts?userId='the user id'.

        Both of the above examples use user id, but one's for chatting, and one's for
        viewing posts. So to differentiate, we just have parameters for what thing you'd like
        to do, so we know what to open

        If no parameters are given, the app is just opened to it's normal home page.
        If we can't figure out what specific thing to do, we'll just open roblox://
        and give the parameters as parameters there, and hope roblox can figure it out

        I'm not going to implemenet every thing both roblox players support, so if
        you need some functionality that isn't supported here (after all, what I
        have here so far is pretty basic), please use command_override, which
        will let you just run your own uri

        for info on how to use it, I found here quite helpful: https://github.com/RoSeal-Extension/Roblox-DeepLink-Parser
        
        :param int place_id: The game (or place) to join when opening the app
        :param str game_instance_id: The game instance to join, you can get server info by using Roblox's api (https://games.roblox.com/v1/games/[game or place id]/servers/[you need to have text here, but it doesn't matter what]), or using our wrapper for it we implemented here
        '''
        # NOTE: All the parameters were grabbed from the following:
        # https://github.com/bloxstraplabs/bloxstrap/wiki/A-deep-dive-on-how-the-Roblox-bootstrapper-works#starting-roblox and
        # https://github.com/RoSeal-Extension/Roblox-DeepLink-Parser
        # so thanks peoples who made those! Not sure what a deeplink is, but I'll take whatever I can get
        
        # constructing the url to open
        url = 'roblox://'

        # we also keep track if we've already added a ? yet, so
        # we know if we should add &
        parameter_character = '?'

        # adding place id if we should
        if place_id:
            url += f'{parameter_character}placeId={place_id}'
            parameter_character = '&'

        # adding place id if we should
        if game_instance_id:
            url += f'{parameter_character}gameInstanceId={game_instance_id}'
            parameter_character = '&'

        # if the url is still just plain roblox://, then we open roblox://a
        if url == 'roblox://':
            url = 'roblox://navigation/home'

        webbrowser.open(url)