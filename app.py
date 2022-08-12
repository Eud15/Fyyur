#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
#Run: FLASK_APP=app.py FLASK_DEBUG=true flask run
import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from markupsafe import Markup
from flask_migrate import Migrate
import datetime
from config import app

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#
from models import *
def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Convertion function.
#----------------------------------------------------------------------------#
def dateStr(date):
  '''
    converting of  dateTime to string
  '''
  return date.strftime('%Y-%m-%d %H:%M:%S')



#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  location ={}
  data = []
  for venue in venues:
    if venue.city in location:
      location[venue.city].append(venue)
    else:
      location[venue.city] = [venue]
  
  for i, venue_list in location.items():
      data.append({
        "city": venue_list[0].city,
        "state": venue_list[0].state,
        "venues": [{
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0,
          } for venue in venue_list]
      })
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form['search_term']
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(venues),
    "data": [{
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": 0,
    } for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<venue_id>', methods=['GET'])
def show_venue(venue_id):

    venue = Venue.query.get(venue_id)
    if venue is None:
      return not_found_error(404)
    data = {
        'id': venue.id,
        'name': venue.name,
        'genres': venue.genres,
        'city': venue.city,
        'state': venue.state,
        'address': venue.address,
        'phone': venue.phone,
        'website_link': venue.website_link,
        'facebook_link': venue.facebook_link,
        'seeking_talent': venue.seeking_talent,
        'seeking_description': venue.seeking_description,
        'image_link': venue.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0,
    }
    date = datetime.datetime.today()
    shows = Show.query.filter(Show.venue_id==venue_id).all()
    for show in shows:
        if show.date_time >= date:
            data['upcoming_shows_count'] += 1
            data['upcoming_shows'].append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'date_time': format_datetime(str(show.date_time))
            })
        else:
            data['past_shows_count'] += 1
            data['past_shows'].append({
                'artist_id': show.artist.id,
                'artist_name': show.artist.name,
                'artist_image_link': show.artist.image_link,
                'date_time': format_datetime(str(show.date_time))
            })
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  
  form = VenueForm(request.form)
  if form.validate():
    genres = ",".join(request.form.getlist('genres'))
    venue = Venue(name=request.form['name'],
                    city=request.form['city'],
                    state=request.form['state'],
                    address = request.form['address'],
                    phone=request.form['phone'],
                    website_link=request.form['website_link'],
                    seeking_talent = (request.form['seeking_talent'] == "y"),
                    seeking_description = request.form['seeking_description'],
                    facebook_link=request.form['facebook_link'],
                    image_link = request.form['image_link'],
                    genres=genres)

    # TODO: modify data to be the data object returned from db insertion
    try:
      db.session.add(venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
      print(str(e))
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  else:
    flash('An error occurred, try to please fill the form')

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
    venue = Venue.query.get(venue_id)

    if venue == None:
      return not_found_error(404)

    venue.name = venue.name
    db.session.delete(venue)
    flash('Venue ' + venue.name + ' was successfully deleted!')
  except :
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be deleted!')
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  data=[{
    "id": artist.id,
    "name": artist.name,
  } for artist in artists]

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form['search_term']
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(artists),
    "data": [{
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": 0,
    } for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<artist_id>', methods=['GET'])
def show_artist(artist_id):

    artist = Artist.query.get(artist_id)
    if artist is None:
        return not_found_error(404)
    data = {
        'id': artist.id,
        'name': artist.name,
        'genres': artist.genres,
        'city': artist.city,
        'state': artist.state,
        'phone': artist.phone,
        'website_link': artist.website_link,
        'facebook_link': artist.facebook_link,
        'seeking_venue': artist.seeking_venue,
        'seeking_description': artist.seeking_description,
        'image_link': artist.image_link,
        'past_shows': [],
        'upcoming_shows': [],
        'past_shows_count': 0,
        'upcoming_shows_count': 0,
    }
    date = datetime.datetime.today()
    shows = Show.query.filter(Show.artist_id==artist_id).all()
    for show in shows:
        if show.date_time >= date:
            data['upcoming_shows_count'] += 1
            data['upcoming_shows'].append({
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'date_time': format_datetime(str(show.date_time))
            })
        else:
            data['past_shows_count'] += 1
            data['past_shows'].append({
                'venue_id': show.venue.id,
                'venue_name': show.venue.name,
                'venue_image_link': show.venue.image_link,
                'date_time': format_datetime(str(show.date_time))
            })
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_data = Artist.query.get(artist_id)
  if artist_data is None:
    return not_found_error(404)

  artist={
    "id": artist_data.id,
    "name": artist_data.name,
    "genres": artist_data.genres.split(','),
    "city": artist_data.city,
    "state": artist_data.state,
    "phone": artist_data.phone,
    "website_link": artist_data.website_link,
    "facebook_link": artist_data.facebook_link,
    "seeking_venue": artist_data.seeking_venue,
    "seeking_talent": artist_data.seeking_description,
    "image_link": artist_data.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)

  if artist is None:
    return not_found_error(404)

  artist.name = request.form['name']
  artist.genres = ",".join(request.form.getlist('genres'))
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.facebook_link = request.form['facebook_link']
  artist.website_link = request.form['website_link']
  artist.seeking_venue = request.form['seeking_venue']
  artist.seeking_description = request.form['seeking_description']
  
  try:
    db.session.commit()
    flash('Artist ' + artist.name + ' was successfully updated!')
  except Exception as e:
    print(str(e))
    db.session.rollback()
    flash('An error occurred. Artist ' + artist.name + ' could not be updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_data = Venue.query.get(venue_id)

  if venue_data is None:
    return not_found_error(404)

  venue={
    "id": venue_data.id,
    "name": venue_data.name,
    "genres": venue_data.genres.split(','),
    "city": venue_data.city,
    "state": venue_data.state,
    "phone": venue_data.phone,
    "website_link": venue_data.website_link,
    "facebook_link": venue_data.facebook_link,
    "seeking_talent": venue_data.seeking_talent,
    "seeking_description": venue_data.seeking_description,
    "image_link": venue_data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  venue = Venue.query.get(venue_id)

  if venue is None:
    return not_found_error(404)

  venue.name = request.form['name']
  venue.genres = ",".join(request.form.getlist('genres'))
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.facebook_link = request.form['facebook_link']
  venue.website_link = request.form['website_link']
  venue.seeking_talent = request.form['seeking_talent']
  venue.seeking_description = request.form['seeking_description']
  
  try:
    db.session.commit()
    flash('Venue ' + venue.name + ' was successfully updated!')
  except Exception as e:
    print(str(e))
    db.session.rollback()
    flash('An error occurred. Venue ' + venue.name + ' could not be updated!')
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead

  form = ArtistForm(request.form)
  if form.validate():
    genres = ",".join(request.form.getlist('genres'))
    artist = Artist(name=request.form['name'],
                  city=request.form['city'],
                  state=request.form['state'],
                  phone=request.form['phone'],
                  website_link = request.form['website_link'],
                  seeking_venue = (request.form['seeking_venue'] == "y"),
                  seeking_description = request.form['seeking_description'],
                  facebook_link=request.form['facebook_link'],
                  image_link = request.form['image_link'],
                  genres=genres)

    # TODO: modify data to be the data object returned from db insertion
    try:
      db.session.add(artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    except Exception as e:
      print(str(e))
      db.session.rollback()
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  else:
    flash('An error occurred, try to please fill the form')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  results = db.session.query(Venue).join(Show, Venue.id == Show.venue_id).join(Artist, Artist.id == Show.artist_id)\
  .with_entities(Venue.id,Venue.name, Artist.id,Artist.name,Artist.image_link, Show.date_time)\
  .order_by(Show.date_time).all()
  data=[{
    "venue_id": result[0],
    "venue_name": result[1],
    "artist_id": result[2],
    "artist_name": result[3],
    "artist_image_link": result[4],
    "start_time": dateStr(result[5])
  } for result in results]
  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  venue_id = request.form['venue_id']
  artist_id = request.form['artist_id']
  date_time = datetime.datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')
  venue = Venue.query.filter(Venue.id == venue_id).all()
  artist = Artist.query.filter(Artist.id == artist_id).all()
  if len(venue) == 0:
    flash('Venue id does not exsit!')
  elif len(artist) == 0:
    flash('Artist id does not exsit!')
  else:
    try:
      show = Show(venue_id=venue_id, artist_id=artist_id, date_time=date_time)
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except Exception as e:
      print(str(e))
      db.session.rollback()
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Show could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
