import obspython as obs
import datetime

target_time = ""
source_name = ""
default_text = ""
target = None


# ------------------------------------------------------------

def string_to_datetime(timestring: str) -> datetime:
    global target
    hours, minutes = timestring.strip().split(":")
    hours, minutes = int(hours), int(minutes)
    now = datetime.datetime.now()
    target = now.replace(hour=hours, minute=minutes, second=0)
    if now.hour * 60 + now.minute > hours * 60 + minutes:
        target = target + datetime.timedelta(days=1)
    return target


def get_diff_second(target_dt: datetime.datetime):
    now = datetime.datetime.now()
    diff: datetime.timedelta = target_dt - now
    total_seconds = int(diff.total_seconds())
    return total_seconds


def get_current_timer_text(diff_seconds: int):
    if diff_seconds < 0:
        return None
    hours = diff_seconds // 3600
    minutes = (diff_seconds % 3600) // 60
    seconds = diff_seconds % 60
    text = f"{minutes:02}:{seconds:02}"
    text = f"{hours:02}:{text}" if hours else text
    return text


def update_text(text: str):
    global source_name
    source = obs.obs_get_source_by_name(source_name)

    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", text)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)

        obs.obs_source_release(source)


def update():
    global target
    global default_text
    total_time = get_diff_second(target)
    text = default_text if total_time < 0 else get_current_timer_text(total_time)
    update_text(text)


# ------------------------------------------------------------

def script_description():
    return (
        "Accepts a user-defined time and counts down to the specified moment.\n"
        "Time format: HH:MM\n"
        "\nBy Tsaplya"
    )


def update_timer(props, prop):
    global source_name
    global target
    global target_time
    if source_name != "" and len(target_time) >= 5:
        obs.timer_remove(update)
        target = string_to_datetime(target_time)
        obs.timer_add(update, 100)
        obs.script_log(obs.LOG_INFO, f"start timer to f{target_time}")


def stop_timer(props, prop):
    obs.timer_remove(update)


def script_update(settings):
    global source_name
    global target
    global target_time
    global default_text
    source_name = obs.obs_data_get_string(settings, "source")
    default_text = obs.obs_data_get_string(settings, "default_text")
    target_time = obs.obs_data_get_string(settings, "target_time")


def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "target_time", "19:00")
    obs.obs_data_set_default_string(settings, "default_text", "COMING SOON")


def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "target_time", "TIME", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "default_text", "TEXT", obs.OBS_TEXT_DEFAULT)

    p = obs.obs_properties_add_list(props, "source", "Text Source", obs.OBS_COMBO_TYPE_EDITABLE,
                                    obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p, name, name)

        obs.source_list_release(sources)

    obs.obs_properties_add_button(props, "button1", "Run", update_timer)
    obs.obs_properties_add_button(props, "button2", "Stop", stop_timer)
    return props
