from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404 # HttpResponse
from django.db.models import F, Q, Avg
from django.db.models.query import EmptyQuerySet
#from django.template import loader
from .models import Survey, Anime, AnimeName, Response, ResponseAnime
from datetime import datetime


# ======= VIEWS =======
# Index
def index(request):
    survey_list = Survey.objects.order_by('year', 'season', 'is_preseason')
    context = {
        'survey_list': survey_list,
    }

    return render(request, 'survey/index.html', context)


# Survey page, use form() if survey active, otherwise use results()
def survey(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    if survey.is_ongoing:
        return form(request, survey)
    else:
        return results(request, survey)

def form(request, survey):
    _, anime_series_list, special_anime_list = get_survey_anime(survey)

    def modify(anime):
        names = anime.animename_set.all()

        anime.japanese_name = names.filter(anime_name_type=AnimeName.AnimeNameType.JAPANESE_NAME, official=True).first()
        anime.english_name  = names.filter(anime_name_type=AnimeName.AnimeNameType.ENGLISH_NAME , official=True).first()
        anime.short_name    = names.filter(anime_name_type=AnimeName.AnimeNameType.SHORT_NAME   , official=True).first()

        return anime

    anime_series_list = [modify(anime) for anime in anime_series_list]

    context = {
        'survey': survey,
        'anime_series_list': anime_series_list,
        'special_anime_list': special_anime_list,
    }
    return render(request, 'survey/form.html', context)

def results(request, survey):
    response_anime_list = ResponseAnime.objects.filter(response__survey=survey)
    response_list = Response.objects.filter(survey=survey)
    response_count = max(response_list.count(), 1)

    _, anime_series_list, special_anime_list = get_survey_anime(survey)

    response_anime_list_per_anime = {anime: response_anime_list.filter(anime=anime, watching=True) for anime in anime_series_list}

    popularity_data = [(anime, response_anime_list_per_anime[anime].count() / response_count * 100.0) for anime in anime_series_list]
    popularity_table = {
        "title": "Most Popular Anime",
        "headers": ["Anime", "%"],
        "data": popularity_data,
    }

    gender_popularity_disparity_data = [(anime, response_anime_list_per_anime[anime].filter(response__gender=Response.Gender.MALE).count() / max(1.0, response_anime_list.filter(anime=anime, watching=True, response__gender=Response.Gender.FEMALE).count())) for anime in anime_series_list]
    gender_popularity_disparity_table = {
        "title": "Biggest Gender Popularity Disparity",
        "headers": ["Anime", "M:F Ratio"],
        "data": gender_popularity_disparity_data,
    }

    score_data = [(anime, response_anime_list_per_anime[anime].filter(score__isnull=False).aggregate(Avg('score'))['score__avg']) for anime in anime_series_list]
    score_data = [(anime, 0.0 if score is None else score) for (anime, score) in score_data]
    score_table = {
        "title": "Most Anticipated Anime" if survey.is_preseason else "Best Anime",
        "headers": ["Anime", "Score"],
        "data": score_data,
    }

    table_list = [popularity_table, gender_popularity_disparity_table, score_table]
    context = {
        'survey': survey,
        'table_list': table_list,
    }
    return render(request, 'survey/results.html', context)



# POST requests will be sent here
def submit(request, year, season, pre_or_post):
    survey = get_survey_or_404(year, season, pre_or_post)
    if request.method == 'POST' and survey.is_ongoing:
        anime_list, _, _ = get_survey_anime(survey)

        response = Response(
            survey=survey,
            timestamp=datetime.now(),
            age=try_get_response(request, 'age', lambda x: int(x), 0),
            gender=try_get_response(request, 'gender', lambda x: Response.Gender(x), ''),
        )
        response.save()

        response_anime_list = []
        for anime in anime_list:
            if survey.is_ongoing and str(anime.id) + '-watched' not in request.POST.keys():
                continue
            response_anime = ResponseAnime(
                response=response,
                anime=anime,
                watching=try_get_response(request, str(anime.id) + '-watched', lambda _: True, False),
                score=try_get_response(request, str(anime.id) + '-score', lambda x: int(x), None),
                underwatched=try_get_response(request, str(anime.id) + '-underwatched', lambda _: True, False),
                expectations=try_get_response(request, str(anime.id) + '-expectations', lambda x: ResponseAnime.Expectations(x), ''),
            )
            response_anime_list.append(response_anime)
        
        ResponseAnime.objects.bulk_create(response_anime_list)
        
        return redirect('survey:index')
    else:
        raise Http404()



# ======= HELPER METHODS =======
def get_survey_anime(survey):
    current_year_season = survey.year * 10 + survey.season
    year_season_filter = Q(start_year_season__lte=current_year_season) & \
        (Q(end_year_season__gte=current_year_season) | Q(end_year_season=None))

    anime_list = Anime.objects.annotate(
        start_year_season  = F('start_year')  * 10 + F('start_season') ,
        end_year_season    = F('end_year')    * 10 + F('end_season')   ,
        subbed_year_season = F('subbed_year') * 10 + F('subbed_season'),
    ).filter(
        year_season_filter
    )

    anime_series_filter = Q(anime_type=Anime.AnimeType.TV_SERIES) | Q(anime_type=Anime.AnimeType.ONA_SERIES) | Q(anime_type=Anime.AnimeType.BULK_RELEASE)
    special_anime_filter = ~anime_series_filter & Q(subbed_year_season=current_year_season)
    
    anime_series_list = anime_list.filter(
        anime_series_filter
    )
    special_anime_list = anime_list.filter(
        special_anime_filter
    )
    combined_anime_list = anime_list.filter(
        anime_series_filter | special_anime_filter
    )
    return combined_anime_list, anime_series_list, special_anime_list

def get_survey_or_404(year, season, pre_or_post):
    if pre_or_post == 'pre':
        is_preseason = True
    elif pre_or_post == 'post':
        is_preseason = False
    else:
        raise Http404("Survey does not exist!")

    survey = get_object_or_404(Survey, year=year, season=season, is_preseason=is_preseason)
    return survey

def try_get_response(request, item, conversion=None, value_if_none=None):
    if item not in request.POST.keys() or request.POST[item] == '':
        return value_if_none
    else:
        if conversion is None:
            return None
        else:
            return conversion(request.POST[item])
