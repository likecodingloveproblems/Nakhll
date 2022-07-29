"""Interaction with Aparat API

Aparat API is a video sharing platform that allows you to upload and share videos.
this module is used to interact with Aparat API using this documentation:
https://aparat.com/api

"""
from __future__ import annotations
import requests
import hashlib
from enum import Enum


class AparatLoginException(Exception):
    """Exception raised when login to Aparat API failed"""


class AparatInvalidResponseException(Exception):
    """Exception raised when Aparat API returns invalid response"""


class AparatUploadVideoException(Exception):
    """Exception raised when Aparat API returns invalid response"""


class AparatCostTypes(Enum):
    FREE = "free"


class AparatWatchActions(Enum):
    WATCH = "watch"
    LOGIN = "login"


class AparatResponseTypes(Enum):
    SUCCESS = "success"
    ERROR = "error"
    VALIDATE_ERROR = 'validateError'


class AparatPaginator:
    def __init__(self) -> None:
        self.items: list = []
        self.next_page: str = None
        self.previous_page: str = None
        self.current_page: int = 1

    def get_next_page_items(self) -> list:
        if self.next_page is None:
            return []
        response = requests.get(self.next_page)
        if response.status_code != 200:
            raise AparatInvalidResponseException(
                f"Aparat API returned invalid response: {response.status_code}"
            )
        self.current_page += 1
        return self.parse_response(response.json())

    def get_previous_page_items(self) -> list:
        if self.previous_page is None:
            return []
        response = requests.get(self.previous_page)
        if response.status_code != 200:
            raise AparatInvalidResponseException(
                f"Aparat API returned invalid response: {response.status_code}"
            )
        self.current_page -= 1
        return self.parse_response(response.json())


class AparatResponse:
    def __init__(self) -> None:
        self.data = None
        self.method_name = None
        self.next_page = None
        self.previous_page = None

    @classmethod
    def parse_response(cls, response: dict, method_name: str) -> AparatResponse:
        response_class = cls()
        response_class.data = response[method_name]
        response_class.method_name = method_name
        if response.get('ui') is not None:
            response_class.next_page = response['ui']['pagingForward']
            response_class.previous_page = response['ui']['pagingBack']
        return response_class

    @property
    def is_paginated(self) -> bool:
        return self.next_page is not None or self.previous_page is not None

    @property
    def is_paginated(self) -> bool:
        pass


class AparatRequestHandler:
    """Given a video path, this class should upload the video to aparat and return the video url"""
    BASE_URL = "https://aparat.com/etc/api/"

    @staticmethod
    def _send_request(data: dict, method_name: str, *, url: str = None, http_method: str = 'get',
                      file_path=None, form_file_name: str = None) -> AparatResponse:
        request_data = '/'.join([f"{key}/{value}" for key, value in data.items()])
        url = url or f"{AparatRequestHandler.BASE_URL}{method_name}/{request_data}"
        if http_method == 'get':
            response = requests.get(url)
        else:
            headers = {'Content-type': 'multipart/form-data'}
            response = requests.post(url,
                                     data=data,
                                     headers=headers,
                                     files={form_file_name: open(file_path, 'rb')})
        if response.status_code != 200:
            raise AparatInvalidResponseException()
        try:
            data = response.json()
        except Exception as ex:
            raise AparatInvalidResponseException()
        return AparatResponse.parse_response(data, method_name)


class AparatVideoTag:
    def __init__(self) -> None:
        self.name: str = None
        self.count: int = None


class AparatUploadVideoFormAction(AparatRequestHandler):
    def __init__(self, profile: AparatProfile) -> None:
        self.action_url: str = None
        self.form_id = None
        method_name = 'uploadform'
        data = {
            'luser': profile.username,
            'ltoken': profile.token,
        }
        aparat_response = self._send_request(data, method_name=method_name)
        self._parse_response_to_form_action(aparat_response)

    def _parse_response_to_form_action(self, response: AparatResponse) -> AparatUploadVideoFormAction:
        data = response.data
        self.action_url = data.get('formAction')
        self.form_id = data.get('frm-id')


class AparatProfile:
    def __init__(self) -> None:
        self.username = None
        self.email = None
        self.user_id = None
        self.name = None
        self.video_count = None
        self.picture_small_url = None
        self.picture_medium_url = None
        self.picture_big_url = None
        self.aparat_url = None
        self.followers_count = None
        self.followed_count = None
        self.description = None
        self.official = None
        self.cloob = None
        self.lenzor = None
        self.twitter = None
        self.facebook = None
        self.follow_link = None
        self.follow_status = None
        self.cover_url = None
        self.has_live = None
        self.profile_videos = None
        self.token = None
        self.mobile_number = None
        self.mobile_valid = None
        self.is_banned = None
        self.categories = None

    def __str__(self) -> str:
        return self.username


class AparatProfileAPI(AparatRequestHandler):

    def login(self, user: str, password: str) -> AparatProfile:
        hashed_password = self._hash_password(password)
        data = {
            "luser": user,
            "lpass": hashed_password,
        }
        aparat_response = self._send_request(data, method_name="login")
        return self._parse_response_to_profile(aparat_response)

    def user_by_search(self, search: str) -> None:
        raise NotImplementedError()

    def profile_categories(self) -> None:
        raise NotImplementedError()

    @classmethod
    def get_profile(cls, username) -> AparatProfile:
        pass

    @staticmethod
    def _hash_password(password: str) -> str:
        md5_password = hashlib.md5(password.encode("utf-8")).hexdigest()
        sha1_md5_password = hashlib.sha1(md5_password.encode("utf-8")).hexdigest()
        return sha1_md5_password

    @staticmethod
    def _parse_response_to_profile(aparat_response: AparatResponse) -> AparatProfile:
        data = aparat_response.data
        if not data.get('type') == AparatResponseTypes.SUCCESS.value:
            raise AparatLoginException()
        profile = AparatProfile()
        profile.username = data.get('username')
        profile.token = data.get('ltoken')
        profile.username = data.get('username')
        profile.name = data.get('name')
        profile.is_banned = data.get('banned') == 'yes'
        profile.user_id = data.get('id')
        profile.email = data.get('email')
        profile.mobile_number = data.get('mobile_number')
        profile.mobile_valid = data.get('mobile_valid')
        profile.picture_small_url = data.get('pic_s')
        profile.picture_medium_url = data.get('pic_m')
        profile.picture_big_url = data.get('pic_b')
        return profile


class AparatVideo:
    def __init__(self) -> None:
        self.id: int = None
        self.title: str = None
        self.username: str = None
        self.user_id: int = None
        self.visit_count: int = None
        self.uid: str = None
        self.process: str = None
        self.sender_name: str = None
        self.big_poster_url: str = None
        self.small_poster_url: str = None
        self.profile_photo_url: str = None
        self.duration: int = None
        self.send_date: str = None
        self.frame_url: str = None
        self.is_official: bool = None
        self.tags: list[AparatVideoTag] = None
        self.description: str = None
        self.category_id: int = None
        self.category_name: str = None
        self.is_autoplay: bool = None
        self.is_360d: bool = None
        self.has_comment: str = None
        self.has_comment_text: str = None
        self.size: int = None
        self.watch_action: AparatWatchActions = None
        self.cost_type: AparatCostTypes = None
        self.can_download: bool = None
        self.like_count: int = None
        self.logged_in_profile: AparatProfile = None

    def __str__(self) -> str:
        return self.title

    def delete_from_server(self) -> None:
        pass


class AparatVideoAPI(AparatRequestHandler):

    def get_video(self, video_uid: str) -> AparatVideo:
        method_name = 'video'
        data = {
            'videohash': video_uid
        }
        aparat_response = self._send_request(data, method_name=method_name)
        return self._parse_response_to_video(aparat_response)

    def get_category_videos(self, category_id: int, per_page: int = None) -> AparatPaginator:
        pass

    def user_videos(self, username: str, per_page: int = None) -> AparatPaginator:
        pass

    def get_video_comments(self) -> list[str]:
        pass

    def search_video(self, search: str, per_page: int = None) -> AparatPaginator:
        pass

    def tag_videos(self, tag_name: str, per_page: int = None) -> AparatPaginator:
        pass

    def upload_video(self, video_path: str, title: str, category: int, form: AparatUploadVideoFormAction, tags: list[str] = None,
                     allow_comment: bool = None, description: str = None, is_draft: bool = None) -> AparatVideo:
        data = {
            'frm-id': form.form_id,
            'data[title]': title,
            'data[category]': category,
            'data[tags]': '-'.join(tags),
            'data[comment]': 'yes' if allow_comment else 'no',
            'data[descr]': description,
            'data[video_pass]': is_draft
        }
        aparat_response = self._send_request(data, method_name='uploadpost', url=form.action_url, http_method='post',
                                             file_path=video_path, form_file_name='video')
        data = aparat_response.data
        if data.get('type') != AparatResponseTypes.SUCCESS.value:
            raise AparatUploadVideoException("Failed to upload video to aparat")
        uid = aparat_response.data.get('uid')
        return self.get_video(uid)

    def _parse_response_to_video(self, response: AparatResponse) -> AparatVideo:
        data = response.data
        tags = []
        tags_data = data.pop('tags', [])
        for tag_data in tags_data:
            tag = AparatVideoTag()
            tag.name = tag_data.get('name')
            tag.count = tag_data.get('cnt')
            tags.append(tag)

        video = AparatVideo()
        video.id = data.get('id')
        video.title = data.get('title')
        video.username = data.get('username')
        video.user_id = data.get('userid')
        video.visit_count = data.get('visit_cnt')
        video.uid = data.get('uid')
        video.process = data.get('process')
        video.sender_name = data.get('sender_name')
        video.big_poster_url = data.get('big_poster')
        video.small_poster_url = data.get('small_poster')
        video.profile_photo_url = data.get('profilePhoto')
        video.duration = data.get('duration')
        video.send_date = data.get('sdate')
        video.frame_url = data.get('frame')
        video.is_official = data.get('official') == 'yes'
        video.tags = tags
        video.description = data.get('description')
        video.category_id = data.get('cat_id')
        video.category_name = data.get('cat_name')
        video.is_autoplay = data.get('autoplay')
        video.is_360d = data.get('360d')
        video.has_comment = data.get('has_comment') == 'yes'
        video.has_comment_text = data.get('has_comment_txt')
        video.size = data.get('size')
        video.watch_action = data.get('watch_action', {}).get('type')
        video.cost_type = data.get('cost_type', {}).get('type')
        video.can_download = data.get('can_download')
        video.like_count = data.get('like_cnt')
        return video


class AparatAPI(AparatRequestHandler):
    def __init__(self, profile: AparatProfile = None, username: str = None, password: str = None) -> None:
        self.profile_api = AparatProfileAPI()
        self.video_api = AparatVideoAPI()
        assert (
            profile is None and username is None and password is None
            or profile and username is None and password is None
            or profile is None and username and password
        ), (
            "You can either pass a profile object or a username and password to login"
        )
        self.profile = profile
        if username and password:
            self.login(username, password)

    def login(self, username, password) -> None:
        self.profile = self.profile_api.login(username, password)

    @property
    def is_authenticated(self):
        return self.profile is not None and self.profile.token is not None

    def upload_video(self, video_path: str, title: str, category: int,
                     tags: list[AparatVideoTag] = None, allow_comment: bool = None,
                     description: str = None, is_draft: bool = False) -> AparatVideo:
        if not self.is_authenticated:
            raise AparatLoginException("Please login to perform this action")
        form = AparatUploadVideoFormAction(self.profile)
        video = self.video_api.upload_video(
            video_path,
            title,
            category,
            form,
            tags,
            allow_comment,
            description,
            is_draft
        )
        return video


if __name__ == "__main__":
    aparat = AparatAPI()
    # print(aparat.is_authenticated)
    aparat.login("m.hassani.de", "mohsenh9735")
    print(aparat.is_authenticated)
    # video = aparat.video_api.get_video('rzKus')
    video = aparat.upload_video('ap.mp4', 'test', 16, [], True, 'test', False)
    print(video)
