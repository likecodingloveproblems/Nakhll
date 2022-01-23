import io
import jdatetime
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.http import JsonResponse

from django.contrib.auth.models import User

from .models import Shop, Profile, Product, Alert

from django.http.response import HttpResponse

from xlsxwriter.workbook import Workbook
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.conf import settings
