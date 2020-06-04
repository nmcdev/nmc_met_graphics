# _*_ coding: utf-8 _*_

# Copyright (c) 2020 NMC Developers.
# Distributed under the terms of the GPL V3 License.

import threading
import streamlit as st
from streamlit.ScriptRequestQueue import RerunData
from streamlit.ScriptRunner import RerunException
from streamlit.server.Server import Server
import streamlit.ReportThread as ReportThread


def is_running_in_streamlit():
    """
    Function to detect if the current script is running inside Streamlit
    refer to https://gist.github.com/tvst/f6ab192d4952757959f026007aadef6a
    """
    thread = threading.current_thread()
    return type(thread).__module__.startswith('streamlit.')

def rerun():
    """Rerun a Streamlit app from the top!
    refer to https://gist.github.com/tvst/58c42300d3b6de48e805af7429cac2e7
    """
    widget_states = _get_widget_states()
    raise RerunException(RerunData(widget_states))


def _get_widget_states():
    # Hack to get the session object from Streamlit.

    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_infos.values()

    for session_info in session_infos:
        if session_info.session._main_dg == ctx.main_dg:
            session = session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')
    # Got the session object!

    return session._widget_states

    ctx = ReportThread.get_report_ctx()

    session = None
    session_infos = Server.get_current()._session_infos.values()

    for session_info in session_infos:
        if session_info.session._main_dg == ctx.main_dg:
            session = session_info.session

    if session is None:
        raise RuntimeError(
            "Oh noes. Couldn't get your Streamlit Session object"
            'Are you doing something fancy with threads?')
    # Got the session object!

    return session._widget_states


st.rerun = rerun