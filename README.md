# Social Media

## About project:
This is the Social Media project API platform for creating managing user accounts, posts, comments, likes, unlikes, follows and unfollows.

## Technologies that implemented in this project:
1. **Django REST Framework** - for managing API views;
2. **PostgreSQL** - the database;
3. **Docker Compose** - for developing the microservices;
4. **Swagger & Redoc** - for API documentation.

## THe main features:
* JWT authentication;
* Logout;
* Allow users to create, delete and managing their profiles, view another users profiles, update information and upload pictures;
* Users can creat

## How to run:
### Using Docker

- Clone the repository: https://github.com/RomanNest/social-media-api.git
- Navigate to the project directory: 
```bash
cd social_media_api
```
- Copy .env.sample to .env and fill all required data
- Build and run Docker container:
``` bash
docker-compose up --build
```
- Create admin user (optional):
``` bash
docker-compose exec -ti social_media python manage.py createsuperuser
```
- Access the API endpoints via: http://localhost:8001

### Using GitHub

- - Clone the repository: https://github.com/RomanNest/social-media-api.git
- Navigate to the project directory: 
```bash
cd social_media_api
```
- Install the Python dependencies:
```bash
pip instal -r requirements.txt
```
- Apply database migrations:
```bash
python manage.py migrate
```
- Run the development server:
```bash
python manage.py runserver
```
- Access the API endpoints via: http://localhost:8000

## API Endpoints
- **Hashtags**: `/api/social_media/hastags/`
- **Posts**: `/api/social_media/posts/`
- **Likes**: `/api/social_media/likes/`
- **Comments**: `/api/social_media/comments/`
- **Follows**: `/api/social_media/follows/`
- **Users**: `/api/user/register`,`/api/user/me` `/api/user/token`, `/api/user/token/refresh`, `/api/user/token/verify`, `/api/user/users`

Each endpoint supports various operations such as listing, creation, retrieval, and updating of resources.
