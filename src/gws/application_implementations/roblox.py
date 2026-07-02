from gws._typing import WindowManagerLike
from gws.window import BasicWindow
from gws._errors import FailedNetworkRequest, WindowNotFoundError
import requests
import webbrowser
import threading
import time

class RobloxWindow(BasicWindow):
    def __init__(self, window_manager: WindowManagerLike, id: str | None = None):
        self.roblox_thread = None
        super().__init__(window_manager, id)
    
    def list_servers(self, place_id: int, sort = 'Desc', exclude_full_servers: bool = False, limit: int = 25, pages: int = 1) -> list[dict]:
        '''Calls the roblox API to list availible servers for a game. This returns limit servers per page, and can request as many pages as there are availbile on the API. Stops automatically if there
        are no more pages to look at

        NOTE: It's not really recommended to get too many pages, or send too many requests in general, as you can get rate limited quite fast
        
        For reference, the endpoint called is: https://games.roblox.com/v1/games/[game id]/servers/public (public because it's a public server)
        
        :param int place_id: The ID of the place (or game) to list servers for
        :param str sort: How the servers should be sorted. Options are: "Desc" (from fullest to emptiest), and "Asc" (from emptiest to fullest)
        :param bool exclude_full_servers: If results should include servers with the max amount of players
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
            'GuestData': 'UserID=-1234567'
        }
        
        for i in range(pages):
            # constructing the full url to request
            request_location = f'https://games.roblox.com/v1/games/{place_id}/servers/public?limit={limit}&sortOrder={sort}&excludeFullGames={exclude_full_servers}'

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

    def open(
            self,
            # I've seperated the following into 3 sections:
            # what we should do on the app
            # parameters for the app
            # and tweaks for this method
            # I did this because it was a lot for me to look at,
            # not sure if this is proper practices, but oh well
            open_home_page: bool = False,
            join_game: bool = False,
            open_conversations: bool = False,
            open_user_profile: bool = False,
            open_group: bool = False,
            open_game_page: bool = False,
            open_search: bool = False,

            place_id: int | None = None,
            game_instance_id: str | None = None,
            user_id: str | None = None,
            group_id: str | None = None,
            search_query: str | None = None,
            search_type: str | None = None,

            roblox_url: str = 'roblox://',
            command_ovveride: str | None = None,
            roblox_opening_time_timout: int = 45,
            ):
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
        :param bool open_home_page: If roblox should launch into the home page when opening
        :param bool join_game: If roblox should launch into a game when opening
        :param bool open_conversation: If roblox should launch into the conversations page/a conversation with a specific user if user_id is given
        :param bool open_user_profile: If roblox should launch into a users profile. Requires user_id to be set
        :param bool open_group: If roblox should launch into a group page. Requires group_id to be set
        :param bool open_game_page: If roblox should launch into a game's details page
        :param bool open_search: If roblox should launch into the search menu with a given prompt (search_query)
        :param int place_id: The id of a game (place? experience?) to either join if join_game is true, or to view the page for if open_game_page is true
        :param str game_instance_id: The id of a specific server to join, these can be gotten from self.list_servers, and they'll be in the id field
        :param str user_id: The ID of a user to either view (if open_user_profile is true), or open a conversation page with (if open_conversations is true)
        :param str group_id: The id of the group to view (if open_group is true)
        :param str search_query: The query to search if open_search is true
        :param str search_type: The type of thing to search. I haven't tested, but I'd guess it's "Games", "People", "Marketplace", "Communities", "CreatorStore"
        :param str roblox_url: The link to open roblox. By default is "roblox://"
        :param str | None command_override: If the command we would run should be overwritten, and just run command_override instead
        :param int roblox_opening_time_timeout: How long to try to find the roblox window until we just give up and say we couldn't find the roblox window.
        '''
        # NOTE: All the parameters were grabbed from the following:
        # https://github.com/bloxstraplabs/bloxstrap/wiki/A-deep-dive-on-how-the-Roblox-bootstrapper-works#starting-roblox and
        # https://github.com/RoSeal-Extension/Roblox-DeepLink-Parser
        # so thanks peoples who made those! Not sure what a deeplink is, but I'll take whatever I can get
        
        # constructing the url to open
        # first we add parameters
        parameters = {}

        if place_id:
            parameters['placeId'] = place_id

        if game_instance_id:
            parameters['gameInstanceId'] = game_instance_id

        if user_id:
            parameters['userId'] = user_id
        
        if group_id:
            parameters['groupId'] = group_id

        if search_query:
            parameters['keyword'] = search_query

        if search_type:
            parameters['type'] = search_type

        # next we turn those parameters into a string we can use
        parameters_string: str = ''
        # we have query character so we can know if we're supposed to use ?
        # or &

        # iterating over all keys and values and turning them into a str
        query_character = '?'
        for key in parameters.keys():
            # adding the parameter
            parameters_string += f'{query_character}{key}={parameters.get(key)}'

            # changing the query character to & since only the first one should be ?
            query_character = '&'

        # now we construct the url to open
        if command_ovveride:
            url = command_ovveride
        elif open_home_page:
            url = f'{roblox_url}/navigation/home'
        elif join_game:
            url = f'{roblox_url}/experiences/start'
        elif open_conversations:
            url = f'{roblox_url}/navigation/chat'
        elif open_user_profile:
            url = f'{roblox_url}/navigation/profile'
        elif open_group:
            url = f'{roblox_url}/navigation/group'
        elif open_game_page:
            url = f'{roblox_url}/navigation/game_details'
        elif open_search:
            url = f'{roblox_url}/navigation/search'
        # if we can't find anything, we default to the home page
        else:
            url = f'{roblox_url}/navigation/home'

        # opening roblox
        self.roblox_thread = threading.Thread(target=webbrowser.open(url + parameters_string), daemon=True)

        # finding the roblox window and setting it as our ID
        # we check as often as we can for roblox_opening_time_timeout seconds, if nothing opens
        # after that amount of time, we give up
        time_we_started_looking = time.time()
        window = None

        while time_we_started_looking - time.time() < roblox_opening_time_timout and window is None:
            # if there's one called roblox, we take that one
            window = self.window_manager.get_window_from_name('Roblox')
            
            # otherwise, we check if there's one named Sober (A linux roblox client)
            if window is None:
                window = self.window_manager.get_window_from_name('Sober')
            
            # otherwise, if neither of those worked, we just look for one that had roblox in it's name
            if window is None:
                window = self.window_manager.get_window_from_regex('.*Roblox.*')

        # lastly, if we couldn't find anything after all that time, we raise an error
        if window is None:
            raise WindowNotFoundError('We couldn\'t find a roblox window. Did one open?')
        # otherwise we set that window's ID as our own
        else:
            self.id = window.id