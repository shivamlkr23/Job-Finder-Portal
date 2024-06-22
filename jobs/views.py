from django.shortcuts import render, redirect
from . models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from datetime import date
from django.contrib import messages
from django.db import IntegrityError
from django.core.exceptions import ValidationError
def index(request):
    return render(request, "index.html")

def user_login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                try :
                     user1 = Applicant.objects.get(user=user)
               
                     if user1.type == "applicant":
                       login(request, user)
                       return redirect("/user_homepage")
                except Applicant.DoesNotExist:
                        # Handle case when Applicant object is not found
                    pass
            else:
                 
                 thank = True
                 return render(request, "user_login.html", {"thank":thank})
    return render(request, "user_login.html")
   

def user_homepage(request):
    
    if not request.user.is_authenticated:
        return redirect('/user_login/')
    applicant = Applicant.objects.get(user=request.user)
    if request.method=="POST":   
        email = request.POST['email']
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        phone = request.POST['phone']
        gender = request.POST['gender']

         # Check if the new email is already in use by another user
        if User.objects.filter(email=email).exclude(pk=request.user.id).exists():
            thank = "This email is already in use by another user."
            return render(request, "user_homepage.html", {'thank': thank, 'applicant': applicant})

        applicant.user.email = email
        applicant.user.first_name = first_name
        applicant.user.last_name = last_name
        applicant.phone = phone
        applicant.gender = gender
        applicant.save()
        applicant.user.save()

        try:
            image = request.FILES['image']

            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or not image.name.upper().endswith(('.PNG', '.JPG', '.JPEG', '.GIF')):
                messages.success(request, "image invalid")
                return redirect(to='user_homepage')


            applicant.image = image
            applicant.save()
            alert = "This email is already in use by another user."
            return render(request, "user_homepage.html", {'alert': alert, 'applicant': applicant})
        except Exception:
            pass
            # return render(request, "user_homepage.html", {'alert':alert})
        alert = True
        return render(request, "user_homepage.html", {'alert':alert})
    return render(request, "user_homepage.html", {'applicant':applicant})

def all_jobs(request):
    jobs = Job.objects.all().order_by('-start_date')
    applicant = Applicant.objects.get(user=request.user)
    apply = Application.objects.filter(applicant=applicant)
    data = []
    for i in apply:
        data.append(i.job.id)
    return render(request, "all_jobs.html", {'jobs':jobs, 'data':data})

def job_detail(request, myid):
    job = Job.objects.get(id=myid)
    return render(request, "job_detail.html", {'job':job})

def job_apply(request, myid):
    if not request.user.is_authenticated:
        return redirect("/user_login")
    applicant = Applicant.objects.get(user=request.user)
    job = Job.objects.get(id=myid)
    date1 = date.today()
    if job.end_date < date1:
        closed=True
        return render(request, "job_apply.html", {'closed':closed})
    elif job.start_date > date1:
        notopen=True
        return render(request, "job_apply.html", {'notopen':notopen})
    else:
        if request.method == "POST":
            resume = request.FILES['resume']
            Application.objects.create(job=job, company=job.company, applicant=applicant, resume=resume, apply_date=date.today())
            alert=True
            return render(request, "job_apply.html", {'alert':alert})
    return render(request, "job_apply.html", {'job':job})

def all_applicants(request):
    company = Company.objects.get(user=request.user)
    application = Application.objects.filter(company=company)
    return render(request, "all_applicants.html", {'application':application})

def signup(request):
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        username = request.POST['username']
        phone = request.POST['phone']
        gender = request.POST['gender']
        image = request.FILES['image']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        try:

            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or not image.name.upper().endswith(('.PNG', '.JPG', '.JPEG', '.GIF')):
                    alert = "Check if the uploaded file is an image.."
                    return render(request, "signup.html", {'alert': alert, 'applicant': applicant})

            else:
                   # Validate and create user
                   user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password1)
            
                    # Validate and create applicant
                   applicants = Applicant.objects.create(user=user, phone=phone, gender=gender, image=image, type="applicant")
                   
                   messages.success(request, "Profile is successfully created")
                   return redirect(to='user_login')

           
        except IntegrityError:
            messages.error(request, "Username is already taken.")
            return redirect('/signup')

        except Exception as e:
            messages.error(request, f"Check if the uploaded file is an image.")
            return redirect('/signup')

    return render(request, "signup.html")



def company_signup(request):
    if request.method == "POST":   
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        # last_name = request.POST['last_name']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        phone = request.POST['phone']
        # gender = request.POST['gender']
        image = request.FILES['image']
        company_name = request.POST['company_name']

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        try:
              # Check if the email is already in use
            if User.objects.filter(email=email).exists():
                messages.error(request, "Email is already in use.")
                return redirect('/company_signup')

            

            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or not image.name.upper().endswith(('.PNG', '.JPG', '.JPEG', '.GIF')):
                    alert = "Check if the uploaded file is an image.."
                    return render(request, "company_signup.html", {'alert': alert, 'company': company})   

            else:

                   user = User.objects.create_user(first_name=first_name, email=email, username=username, password=password1)
                   company = Company.objects.create(user=user, phone=phone, image=image, company_name=company_name, type="company", status="pending")
                   user.save()
                   company.save()
                   messages.success(request, "Profile is successfully created")
                   return redirect(to='company_login')

        except IntegrityError:
            messages.error(request, "Company is already taken.")
            return redirect('/company_signup')
        except Exception as e:
            messages.error(request, f"image must be .png .jpg .jpeg .gif.")
            return redirect('/company_signup')

    return render(request, "company_signup.html")


def company_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
             try:
                  user1 = Company.objects.get(user=user)
                  if user1.type == "company" and user1.status != "pending" and user1.status != "Rejected":
                     login(request, user)
                     return redirect("/company_homepage")
                  else:
                       alert = True
                       return render(request, "company_login.html", {"alert":alert})
             except Company.DoesNotExist:
                alert = True
                return render(request, "company_login.html", {"alert": alert})
        else:
               alert = True
               return render(request, "company_login.html", {"alert": alert})

    return render(request, "company_login.html")

def company_homepage(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    company = Company.objects.get(user=request.user)
    if request.method=="POST":   
        email = request.POST['email']
        first_name=request.POST['first_name']
        # last_name=request.POST['last_name']
        phone = request.POST['phone']
        # gender = request.POST['gender']

         # Check if the email is already in use by another user
        if User.objects.filter(email=email).exclude(pk=company.user.pk).exists():
            thank = "Email is already in use by another user."
            return render(request, "company_homepage.html", {'company': company, 'thank': thank})

        company.user.email = email
        company.user.first_name = first_name
        # company.user.last_name = last_name
        company.phone = phone
        # company.gender = gender
        company.save()
        company.user.save()

        try:
            image = request.FILES['image']

            if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')) or not image.name.upper().endswith(('.PNG', '.JPG', '.JPEG', '.GIF')):
                     messages.success(request, "image must be .png .jpg .jpeg .gif")
                     return redirect(to='company_homepage')

            else:
                   company.image = image
                   company.save()
                   alert = "Check if the uploaded file is an image.."
                   return render(request, "company_homepage.html", {'alert': alert, 'company': company})
        except:
            pass
        alert = True
           
        return render(request, "company_homepage.html", {'alert':alert})
    return render(request, "company_homepage.html", {'company':company})

def add_job(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    if request.method == "POST":
        title = request.POST['job_title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        salary = request.POST['salary']
        experience = request.POST['experience']
        location = request.POST['location']
        skills = request.POST['skills']
        description = request.POST['description']
        user = request.user
        company = Company.objects.get(user=user)
        job = Job.objects.create(company=company, title=title,start_date=start_date, end_date=end_date, salary=salary, image=company.image, experience=experience, location=location, skills=skills, description=description, creation_date=date.today())
        job.save()
        alert = True
        return render(request, "add_job.html", {'alert':alert})
    return render(request, "add_job.html")

def job_list(request):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    companies = Company.objects.get(user=request.user)
    jobs = Job.objects.filter(company=companies)
    return render(request, "job_list.html", {'jobs':jobs})

from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

def edit_job(request, myid):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    
    try:
        job = Job.objects.get(id=myid)
    except ObjectDoesNotExist:
        return HttpResponse("Job not found", status=404)

    if request.method == "POST":
        title = request.POST['job_title']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        salary = request.POST['salary']
        experience = request.POST['experience']
        location = request.POST['location']
        skills = request.POST['skills']
        description = request.POST['description']

        try:
            # Validate end_date is not less than start_date
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

                if end_date_obj < start_date_obj:
                    thank = "End date must not be less than the start date."
                    return render(request, "edit_job.html", {'job': job, 'thank': thank})
        except ValueError:
            # Handle the case where date parsing fails
            alert = "Invalid date format."
            return render(request, "edit_job.html", {'job': job, 'alert': alert})

        job.title = title
        job.salary = salary
        job.experience = experience
        job.location = location
        job.skills = skills
        job.description = description

        if start_date:
            job.start_date = start_date

        if end_date:
            job.end_date = end_date

        job.save()
        alert = True
        return render(request, "edit_job.html", {'alert': alert})

    return render(request, "edit_job.html", {'job': job})


def company_logo(request, myid):
    if not request.user.is_authenticated:
        return redirect("/company_login")
    job = Job.objects.get(id=myid)
    if request.method == "POST":
        image = request.FILES['logo']
        job.image = image 
        job.save()
        alert = True
        return render(request, "company_logo.html", {'alert':alert})
    return render(request, "company_logo.html", {'job':job})

def Logout(request):
    logout(request)
    return redirect('/')

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        

        if user is not None and user.is_active and user.is_superuser:
            login(request, user)
            return redirect("/all_companies")
        else:
            alert = True
            return render(request, "admin_login.html", {"alert":alert})
    return render(request, "admin_login.html")

def view_applicants(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicants = Applicant.objects.all()
    return render(request, "view_applicants.html", {'applicants':applicants})

def delete_applicant(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    applicant = User.objects.filter(id=myid)
    applicant.delete()
    return redirect("/view_applicants")

def pending_companies(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = Company.objects.filter(status="pending")
    return render(request, "pending_companies.html", {'companies':companies})

def change_status(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    company = Company.objects.get(id=myid)
    if request.method == "POST":
        status = request.POST['status']
        company.status=status
        company.save()
        alert = True
        return render(request, "change_status.html", {'alert':alert})
    return render(request, "change_status.html", {'company':company})

def accepted_companies(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = Company.objects.filter(status="Accepted")
    return render(request, "accepted_companies.html", {'companies':companies})

def rejected_companies(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = Company.objects.filter(status="Rejected")
    return render(request, "rejected_companies.html", {'companies':companies})

def all_companies(request):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    companies = Company.objects.all()
    return render(request, "all_companies.html", {'companies':companies})

def delete_company(request, myid):
    if not request.user.is_authenticated:
        return redirect("/admin_login")
    company = User.objects.filter(id=myid)
    company.delete()
    return redirect("/all_companies")


