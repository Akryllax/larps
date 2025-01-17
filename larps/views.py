from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from .csv_importer import process_csv
from .forms import *
from .views_util import *

# HOME AND LOGOUT

def home_view(request):
    template = 'larps/home.html'
    assigments = CharacterAssigment.objects.filter(user=request.user)
    larps = Larp.objects.all()
    context = {'user': request.user,
               'character_assigments': assigments, 'larps': larps}
    return render(request, template, context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/login')


def not_allowed_view(request):
    template = "larps/not_allowed.html"
    context = {}
    return render(request, template, context)


# PLAYERS MEASUREMENTS

def measurements_form_view(request):
    template = 'larps/measurements_form.html'
    measurements = get_measurements(request.user)
    if request.method == 'POST':
        form = MeasurementsForm(request.POST)
        if form.is_valid():
            measurements.save_profile(form.cleaned_data)
    else:
        data = measurements.get_data()
        form = MeasurementsForm(data)
    assigments = CharacterAssigment.objects.filter(user=request.user)
    larps = Larp.objects.all()
    context = {'form': form, 'character_assigments': assigments, 'larps': larps}
    return render(request, template, context)


# BOOKINGS

def manage_bookings_view(request, larp_id, run):
    template = 'larps/bookings_form.html'
    context = build_context(request, larp_id, run)
    bookings = get_bookings(request.user, context['larp'], run)
    if not bookings:
        url = reverse('larps:home')
        return HttpResponseRedirect(url)
    if request.method == 'POST':
        form = BookingsForm(request.POST, larp_id)
        if form.is_valid():
            bookings.save_bookings(form.cleaned_data)
    else:
        bookings_data = bookings.get_data()
        form = BookingsForm(bookings_data, larp_id)
    context['form'] = form
    return render(request, template, context)


# CHARACTERS

def characters_run_view(request, larp_id, run):
    template = "larps/character_list.html"
    context = build_context(request, larp_id, run)
    context['character_list'] = get_characters(context['larp'])
    return render(request, template, context)


def my_character_view(request, larp_id, run):
    template = "larps/character_detail.html"
    context = build_context(request, larp_id, run)
    return render(request, template, context)


# CSV IMPORTER

def file_upload_view(request):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "csv_import/file_upload.html"
    form = ImportCSVForm()
    context = {'form': form, 'user': request.user}

    if request.method == "POST":
        file = request.FILES['file']
        result = process_csv(file)
        context["result"] = result

    return render(request, template, context)


# UNIFORMS

def uniforms_view(request):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/uniforms.html"
    context = {"uniforms": Uniform.objects.all()}
    return render(request, template, context)


def uniform_sizes_view(request, uniform_id):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/uniforms.html"
    context = {"uniforms": Uniform.objects.all()}
    selected_uniform = Uniform.objects.get(id=uniform_id)
    if selected_uniform.group:
        context["group"] = selected_uniform.group
        players_with_sizes = selected_uniform.get_players_with_recommended_sizes()
        context["players"] = players_with_sizes
        context["sizes"] = selected_uniform.get_sizes_with_quantities(
            players_with_sizes)
    return render(request, template, context)


# ADMINS VIEWS

def missing_info_index_view(request):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/missing_info_index.html"
    larps = Larp.objects.all()
    larps_info = []
    for larp in larps:
        number_of_runs = larp.get_number_of_runs()
        info = {"name": larp.name, "id": larp.id,
                "runs": range(1, number_of_runs+1)}
        larps_info.append(info)

    context = {"larps": larps_info}
    return render(request, template, context)


def players_missing_info_view(request, larp_id):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/missing_info.html"
    larp = Larp.objects.get(id=larp_id)
    players_information = larp.get_players_information()
    context = {"larp": larp.name, "larp_id": larp_id,
                "players_information": players_information}
    return render(request, template, context)


def players_missing_info_by_run_view(request, larp_id, run):
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/missing_info.html"
    larp = Larp.objects.get(id=larp_id)
    players_information_all_runs = larp.get_players_information()
    if run <= len(players_information_all_runs):
        players_information = [players_information_all_runs[run-1]]
    else:
        players_information = []
    context = {"larp": larp.name, "run": run,
               "players_information": players_information}
    return render(request, template, context)


def players_list(request, larp_id = None, run_id = None):
    #Is admin?
    if not request.user.is_staff:
        return not_allowed_view(request)
    template = "larps/player_list.html"

    larps_info = []
    current_larp = []
    current_larp_runs = 0

    if larp_id:
        current_larp = Larp.objects.get(id=larp_id)
    else:
        current_larp = Larp.objects.first()
        larp_id = current_larp.id

    if not run_id:
        run_id = 1

    for larp in Larp.objects.all():
        runs = larp.get_number_of_runs()
        #Reuse loop to get current larp runs
        if current_larp.id == larp.id:
            current_larp_runs = runs

        info = {
            "id": larp.id,
            "name": larp.name,
            "runs": runs
        }
        larps_info.append(info)

    if current_larp:
        players_info_list = current_larp.get_players_list_info(run_id=run_id)
    else:
        players_info_list = None
    context = {
        "selector_status":{
            "larp_id" : larp_id,
            "run_id" : run_id,
            "runs" : range(current_larp_runs)
        },
        "larp_list" : Larp.objects.order_by("id").values(),
        "players_information": players_info_list,
        "table_headers" : [
            "type",
            "fullname",
            "username",
            "email",
            "character",
            "group",
            "race",
            "rank",
            "concept",
            "character sheet",
            "read friendly sheet",
            "discord email"
        ]
    }
    return render(request, template, context)
