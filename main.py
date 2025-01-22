import vk_api
import os
import json
import requests
from alive_progress import alive_bar
from random import shuffle
from time import mktime
from datetime import date, datetime, time, timedelta


def get_post_dt(
    after: datetime, bounds: tuple[time, time], step: timedelta
) -> datetime:
    ## TODO: step > timedelta(days = 1)
    print(f"after={after}\nbounds={bounds}\nstep={step}")
    if bounds[0] < bounds[1]:
        if bounds[0] <= after.time() < bounds[1]:
            post_dt = after + step
            if post_dt.time() > bounds[1] or post_dt.time() < bounds[0]:
                post_dt = datetime.combine(
                    date=after.date() + timedelta(days=1), time=bounds[0]
                )
        else:
            post_dt = datetime.combine(date=after.date(), time=bounds[0])
            if post_dt <= after:
                post_dt += timedelta(days=1)
    else:
        if bounds[1] <= after.time() < bounds[0]:
            post_dt = datetime.combine(date=after.date(), time=bounds[0])
        else:
            post_dt = after + step
            if bounds[1] < post_dt.time() < bounds[0]:
                post_dt = datetime.combine(date=post_dt.date(), time=bounds[0])

    return post_dt


if __name__ == "__main__":
    config = json.load(open("config.json", "r"))

    group_id = int(config["group_id"])
    token = config["token"]
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()

    img_dir = config["img_dir"]
    done_dir = config["done_dir"]
    images = sorted(os.listdir(img_dir), reverse=bool(config["sort_descend"]))
    if bool(config["shuffle"]):
        shuffle(x=images)

    bounds = (
        time(hour=int(config["start"]["hour"]), minute=int(config["start"]["minute"])),
        time(hour=int(config["end"]["hour"]), minute=int(config["end"]["minute"])),
    )
    step = timedelta(hours=config["step"]["hour"], minutes=config["step"]["minute"])

    postponed = vk.wall.get(owner_id=-group_id, filter="postponed", count=1)
    if postponed["count"] > 1:
        postponed = vk.wall.get(
            owner_id=-group_id,
            offset=postponed["count"] - 1,
            filter="postponed",
            count=1,
        )
    if postponed["count"] != 0 and postponed["items"][0]["date"] >= mktime(
        datetime.now().timetuple()
    ):
        post_time = datetime.fromtimestamp(postponed["items"][0]["date"])
    else:
        post_time = datetime.combine(
            date=datetime.now().date() + timedelta(days=1), time=bounds[0]
        )

    total_imgs = len(images)
    with alive_bar(total=total_imgs, force_tty=True) as bar:
        for img in images:
            photo = img_dir + "/" + img
            server = vk.photos.getWallUploadServer(group_id=group_id)
            try:
                post = requests.post(
                    url=server["upload_url"], files={"photo": open(photo, "rb")}
                ).json()
                upload_result = vk.photos.saveWallPhoto(
                    server=post["server"],
                    photo=post["photo"],
                    hash=post["hash"],
                    group_id=group_id,
                )[0]
            except BaseException as e:
                print(f"Upload fail on {img} with exception:\n{e}\n")

            string = (
                f"photo{upload_result["owner_id"]}_{upload_result["id"]}"
            )
            post_time = get_post_dt(after=post_time, bounds=bounds, step=step)
            try:
                vk.wall.post(
                    owner_id=-group_id,
                    attachments=string,
                    from_group=1,
                    publish_date=int(mktime(post_time.timetuple())),
                )
            except vk_api.exceptions.ApiError as e:
                print(f"Error: {e}\n publish_date={post_time}")
            else:
                os.replace(src=photo, dst=done_dir + "/" + img)
            finally:
                bar()
