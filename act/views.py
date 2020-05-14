import datetime
from hashlib import sha1 as sha_constructor
import logging
import re
from urllib.parse import urlencode
import uuid

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .email import email_confirmation, email_main, email_reset
# from .forms import UserLoginForm, UserRegisterForm, UserLoginEmailForm, InvitationKeyForm, InvitationAcceptForm, ResetForm
from lcore.utils import in_post
# from .models import InvitationKey
from .token import account_activation_token
# from the_list.models import ShopGroup


User = get_user_model()


# ############## General functions #####################
# def create_next_increment_name(name):
#     pattern = r"(^[a-zA-Z '-]+)([0-9]+)"
#     match = re.match(pattern, name)
#     if match:
#         increment = match.group(2)
#         new_inc = int(increment) + 1
#         new_name = match.group(1) + str(new_inc)
#         name_length = len(match.group(1))
#
#         if len(new_name) > 30:
#             new_name = match.group(1)[:name_length-1] + str(new_inc)
#         return new_name
#     else:
#         return name + '1'
#
#
# def create_key():
#     salt = uuid.uuid4().hex
#     key = sha_constructor(salt.encode()).hexdigest()
#     logging.getLogger("info_logger").info(f'created key is {key}')
#     return key
#
#
# def is_existing_user(email):
#     if User.objects.filter(email=email).exists():
#         return True
#     else:
#         return False
#
#
# def create_username(first_name, last_name):
#     logging.getLogger("info_logger").info(f'no username yet')
#
#     new_username = first_name[:15] + last_name[:10]
#     new_username.replace(' ', '')
#     this_user = User.objects.all().filter(Q(username__iexact=new_username))
#
#     while this_user.exists():
#         new_username = create_next_increment_name(new_username)
#         this_user = User.objects.all().filter(Q(username__iexact=new_username))
#     return new_username
#
# # ############################## VIEWS #########################
#
#
# def account_activation_sent(request):
#     content_body = ('<p>Thank you for registering!<br>'
#                     'To complete the process, check your mailbox for an email from us, then '
#                     '<br> Click on the link that will bring you back to the site to do so<br><br>'
#                     'See you soon ....</p>')
#     context = {'title': 'Sent email',
#                'content_body': content_body}
#     return render(request, 'activation_sent.html', context)
#
#
# def activate(request, uidb64, token, group):
#     try:
#         logging.getLogger("info_logger").info(f'new user url decode start')
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         new_user = User.objects.get(pk=uid)
#         group_id = force_text(urlsafe_base64_decode(group))
#         new_group = ShopGroup.objects.get(pk=group_id)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         logging.getLogger("info_logger").info(f'user decode failed')
#         new_user = None
#
#     if new_user is not None and account_activation_token.check_token(new_user, token):
#         logging.getLogger("info_logger").info(f'update user and group')
#         new_user.is_active = True
#         new_user.save()
#
#         # activate the group and set the properties required
#         new_group.disabled = False
#         new_group.save()
#         new_group.members.add(new_user)
#         new_group.leaders.add(new_user)
#
#         login(request, new_user)
#         request.session['list'] = new_group.id
#         logging.getLogger("info_logger").info(f'user list set in session')
#         return redirect('set_group')
#     else:
#         return render(request, 'activation_invalid.html')
#
#
# def account_activation_sent(request):
#     content_body = ('<p>Thank you for registering!<br>'
#                     'To complete the process, check your mailbox for an email from us, then '
#                     '<br> Click on the link that will bring you back to the site to do so<br><br>'
#                     'See you soon ....</p>')
#     context = {'title': 'Sent email',
#                'content_body': content_body}
#     return render(request, 'activation_sent.html', context)
#
#
# @login_required()
# def complete(request):
#     template_name = 'invitation_complete.html'
#     mail_body = request.GET.get('send_result')
#     logging.getLogger("info_logger").info(f'Invite Complete|parameter = {mail_body} ')
#     context = {
#         'title': 'Sent invite',
#         'mail_body': mail_body}
#
#     return render(request, template_name, context)
#
#
# @login_required()
# def invite(request):
#     form = InvitationKeyForm(request.user, request.POST or None)
#
#     template_name = 'invitation_form.html'
#     invite_selection = ShopGroup.objects.managed_by(request.user)
#     logging.getLogger("info_logger").info(f'can select from {invite_selection}')
#
#     if request.method == 'POST':
#         logging.getLogger("info_logger").info('Post section | user={request.user}')
#
#         if form.is_valid():
#             InvitationKey = form.save(commit=False)
#             data = request.POST.copy()
#             email = data.get('email')
#
#             InvitationKey.key = create_key()
#             InvitationKey.from_user = request.user
#             InvitationKey.invited_email = email
#             logging.getLogger("info_logger").info('going to save invitation key')
#             InvitationKey.save()
#             send_status=''
#             if not is_existing_user(email):
#                 # not an existing user, attempt to email
#                 email_kwargs = {"key": InvitationKey.key,
#                                 "invitee": data.get('invite_name'),
#                                 "user_name": request.user.username,
#                                 "group_name": InvitationKey.invite_to_group,
#                                 "destination": data.get('email'),
#                                 "subject": "Your invitation to join"}
#                 send_result = email_main(False, **email_kwargs)
#                 # result can be 0 if success or a string if failed
#                 if send_result != 0:
#                     send_result = ('<p>Automatic sending failed.<br>Please copy the text below, paste'
#                                    ' it into a new email and send it to your friend.<br><br></p>') + send_result
#             else:
#                 # 3rd case not sending an email
#                 send_result = ('<p>The person you invited is already a member on the site<br>'
#                                'Next time they log on, they will be able to join the group</p>')
#
#             if send_result != 0:
#                 logging.getLogger("info_logger").info('there is a send_result')
#                 #  send_result contains the body. The below creates a custom url to contain the invite text
#                 base_url = reverse('complete')
#                 query_string = urlencode({'send_result': send_result})
#                 url = f'{base_url}?{query_string}'
#                 return redirect(url)
#             else:
#                 logging.getLogger("info_logger").info("email sent")
#                 return redirect('complete')
#         else:
#             logging.getLogger("info_logger").info("errors on form, return to form")
#             print(f'Form errors: {form.errors}')
#
#     logging.getLogger("info_logger").info('Outside Post section')
#     if not invite_selection:
#         logging.getLogger("info_logger").info('no invite possible - not a manager')
#         form_option = 'refer'
#     else:
#         form_option = 'fill'
#     context = {
#         'title': 'Send invite to join the group',
#         'form': form,
#         'form_option': form_option,
#     }
#     return render(request, template_name, context)
#
#
# def invited(request, key):
#     """
#     For the arrival of an invited user not registered before.
#     will be processing the url data to complete the registration but not with email confirmation
#     since that is done
#     :param key: this is the key in the database and the url
#     :return: inform the user of an invalid key or go through the registration process and then return to set_group
#     """
#     form = InvitationAcceptForm(request.POST or None)
#     # possible outcomes: key is ok and can be used | key is invalid | key is expired | key already used
#     logging.getLogger("info_logger").info(f'testing of the key to start')
#     key_status = 'expired'
#     sender = 'unknown'
#     try:
#         this_key = InvitationKey.objects.get(key=key)
#         sender = this_key.from_user_id
#         if not this_key.invite_used and not this_key.key_expired:
#             key_status = 'ready'
#         elif this_key.invite_used:
#             key_status = 'used'
#         elif this_key.key_expired:
#             key_status = 'expired'
#         logging.getLogger("info_logger").info(f'key is {key_status}')
#
#     except ObjectDoesNotExist:
#         key_status = 'invalid'
#         logging.getLogger("info_logger").info(f'key is {key_status}')
#
#     if key_status in ('used', 'expired', 'invalid'):
#         context = {
#             'title': 'Invite not usable',
#             'status': key_status,
#             'sender': sender, }
#         logging.getLogger("info_logger").info(f'Invalid view to show')
#         return render(request, 'invitation_invalid.html', context)
#
#     template_name = 'invitation_accept.html'
#
#     if request.POST and form.is_valid():
#         logging.getLogger("info_logger").info(f'form validated')
#         the_group = this_key.invite_to_group_id
#         the_user_email = this_key.invited_email
#         first_name = form.cleaned_data['first_name']
#         last_name = form.cleaned_data['last_name']
#         pw = form.cleaned_data['password']
#         username = create_username(first_name, last_name)
#
#         logging.getLogger("info_logger").info(f'create the new user {username}')
#         user = User.objects.create_user(username, the_user_email, pw)
#         user.is_active = True
#         user.first_name = first_name
#         user.last_name = last_name
#         user.save()
#
#         logging.getLogger("info_logger").info(f'Authenticate and log in {username}')
#         user = authenticate(username=username, password=pw)
#         login(request, user)
#
#         logging.getLogger("info_logger").info(f'Update key use')
#         this_key.invite_used = True
#         this_key.registrant = user
#         this_key.save()
#
#         logging.getLogger("info_logger").info(f'Add user to group {the_group}')
#         joining_group = ShopGroup.objects.get(pk=the_group)
#         joining_group.members.add(user)
#
#         return redirect('set_group')
#     else:
#         context = {'title': 'Accept Invite',
#                    'form': form, }
#
#         return render(request, template_name, context=context)
#
#
# @login_required()
# def invite_select_view(request):
#     """
#     when an existing user logs in - check if there are invites
#         no invites - send to set_group
#         invites - show list to accept or decline the invite
#         No more invites - send to set_group
#     """
#     title = 'Select to join group/s'
#     open_invites = InvitationKey.objects.filter(invite_used=False).filter(invited_email=request.user.email)
#
#     if open_invites.count() == 0:
#         logging.getLogger("info_logger").info("redirect to select a group")
#         return redirect('set_group')
#     else:
#         if request.POST:
#             accept_item = in_post(request.POST, 'accept_item')
#             reject_item = in_post(request.POST, 'reject_item')
#             if accept_item != 0 or reject_item != 0:
#                 item_to_update = max(accept_item, reject_item)
#                 instance = get_object_or_404(InvitationKey, id=item_to_update)
#                 if accept_item != 0:
#                     logging.getLogger("info_logger").info(f'to accept item {accept_item}')
#                     group_instance = get_object_or_404(ShopGroup, name=instance.invite_to_group.name)
#                     group_instance.members.add(request.user)
#                     instance.invite_used = True
#                 elif reject_item != 0:
#                     logging.getLogger("info_logger").info(f'to mark as reject item {reject_item}')
#                     instance.invite_used = True
#
#                 instance.save()
#
#     open_invites = InvitationKey.objects.filter(invite_used=False).filter(invited_email=request.user.email)
#
#     if open_invites.count() == 0:
#         # redirect to the other form
#         return redirect('shop:group_select')
#
#     context = {'objects': open_invites,
#                'title': title}
#
#     return render(request, "invite_select_list.html", context=context)
#
#
# def login_view(request):
#     """
#     the view only handles the login and then hands off to invite select or group select views
#
#     """
#     logging.getLogger("info_logger").info(f'entry to view')
#     next = request.GET.get('next')  # this is available when the login required redirected to user to log in
#     form = UserLoginForm(request.POST or None)
#     title = 'Login'
#     if form.is_valid():
#         logging.getLogger("info_logger").info(f'form submitted')
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         login(request, user)
#         logging.getLogger("info_logger").info(f'new user authenticated ? {str(request.user.is_authenticated())}')
#         has_invites = InvitationKey.objects.key_for_email(user.email)
#         if has_invites:
#             logging.getLogger("info_logger").info(f'divert to invite selection')
#             return redirect('invitations:invite_select_view')
#         else:
#             logging.getLogger("info_logger").info(f'divert to set group')
#             return redirect('set_group')
#
#     context = {'form': form,
#                'title': title}
#     return render(request, "login_form.html", context=context)
#

def login_email(request):
    """
    the view only handles the login and then hands off to invite select or group select views
    this method uses the email address and not the username
    """
    logging.getLogger("info_logger").info(f'entry to view')
    next = request.GET.get('next')  # this is available when the login required redirected to user to log in
    return redirect('/')
    # form = UserLoginEmailForm(request.POST or None)
    # title = 'Login'
    # form_mode = 'entry'
    # if request.method == 'POST' and form.is_valid():
    #     logging.getLogger("info_logger").info(f'form submitted')
    #     email = form.cleaned_data.get('email')
    #     password = form.cleaned_data.get('password')
    #     username = form.cleaned_data.get('username')
    #     user = authenticate(username=username, password=password)
    #
    #     if user:
    #         login(request, user)
    #         logging.getLogger("info_logger").info(f'new user authenticated')
    #         has_invites = InvitationKey.objects.key_for_email(user.email)
    #         if has_invites:
    #             logging.getLogger("info_logger").info(f'divert to invite selection')
    #             return redirect('invite_select_view')
    #         else:
    #             logging.getLogger("info_logger").info(f'divert to set group')
    #             return redirect('set_group')
    # elif request.method == 'POST' and not form.is_valid():
    #     email = form.cleaned_data.get('email')
    #     user = User.objects.get(email=email)
    #     if email:
    #         form_mode = 'pw_reset'
    #         #this has to contain the email at least and any password
    #         if 'reset' in request.POST:
    #             coded_user = force_text(urlsafe_base64_encode(force_bytes(user.pk)))
    #             token = account_activation_token.make_token(user)
    #             email_kwargs = {"coded_user": coded_user,
    #                             "token": token,
    #                             "destination": email,
    #                             "subject": "Reset request"}
    #             send_result = email_reset(**email_kwargs)
    #             return redirect('password_link_sent')
    #
    #
    # context = {'form': form,
    #            'title': title,
    #            'mode': form_mode}
    # return render(request, "login_form.html", context=context)

#
# def password_link_sent(request):
#     content_body = ('<p>Reset link sent!<br>'
#                     'To complete the process, check your mailbox for an email from us, then '
#                     '<br> Click on the link that will allow you to reset the password <br><br>'
#                     'See you soon ....</p>')
#     context = {'title': 'Sent email',
#                'content_body': content_body}
#     return render(request, 'activation_sent.html', context)
#
#
# # def password_reset(request, user_email):
# #     logging.getLogger("info_logger").info(f'Enter')
# #     if request.user.is_authenticated:
# #         return redirect('/')
# #     # user is not authenticated, so there is no user object
# #     user_instance = get_object_or_404(User, user=request.user)
# #     if user_instance:
# #         # create the token
# #         pass
# #     else:
# #         pass
#
#
# def password_validation(request, uidb64, token):
#     try:
#         logging.getLogger("info_logger").info(f'existing user url decode start')
#         uid = force_text(urlsafe_base64_decode(uidb64))
#         new_user = User.objects.get(pk=uid)
#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         logging.getLogger("info_logger").info(f'user decode failed')
#         new_user = None
#
#     if new_user is not None and account_activation_token.check_token(new_user, token):
#         logging.getLogger("info_logger").info(f'update user and group')
#         # need a form
#         form = ResetForm(request.POST or None)
#         if request.method == 'POST' and form.is_valid():
#             new_user.password = make_password(form.cleaned_data.get('password2'))  # make_password
#             new_user.save()
#             login(request, new_user)
#             logging.getLogger("info_logger").info(f'user logged in')
#             return redirect('set_group')
#         else:
#             context = {
#                 'form': form,
#
#             }
#             return render(request, 'pw_reset.html', context)
#     else:
#         return render(request, 'activation_invalid.html')
#         # update this to another form or multipurpose
#
#
# @login_required()
# def set_group(request):
#     """ Sets group choice if there is only 1
#     divert to select view if more
#     """
#     list_choices = ShopGroup.objects.filter(members=request.user)
#     if not list_choices:
#         # usually only when startup
#         logging.getLogger("info_logger").info(f'rare case - no groups for user')
#         return redirect('/')
#     elif list_choices.count() > 1:
#         logging.getLogger("info_logger").info(f'user {request.user} is member to >1 group')
#         return redirect('shop:group_select')
#     else:
#         # also set the session with the value
#         select_item = list_choices.first().id
#         logging.getLogger("info_logger").info(f'default list {select_item}')
#         request.session['list'] = select_item
#         return redirect('/')
#
#
def register_view(request):
    """
    register as a complete unknown and uninvited visitor
    settings can disable the view
    """
    logging.getLogger("info_logger").info(f'Enter')
    next = request.GET.get('next')
    if request.user.is_authenticated:
        return redirect('/')
    else:
        return redirect('/')

    # if 'REGISTRATIONS' in dir(settings) and settings.REGISTRATIONS:
    #     logging.getLogger("info_logger").info(f'Registration allowed')
    #     title = 'Register'
    #     form = UserRegisterForm(request.POST or None)
    #     if form.is_valid():
    #         target_group = form.cleaned_data.get('joining')
    #         # to be valid it was checked to not exist
    #
    #         user = form.save(commit=False)
    #         user.is_active = False
    #         user.username = 'blah' # create_username(user.first_name, user.last_name)
    #         password = form.cleaned_data.get('password')
    #         user.set_password(password)
    #         user.backend = 'django.contrib.auth.backends.ModelBackend'
    #         user.save()
    #         logging.getLogger("info_logger").info(f'Saved user')
    #
    #
    #         coded_user = force_text(urlsafe_base64_encode(force_bytes(user.pk)))
    #         coded_group = force_text(urlsafe_base64_encode(force_bytes(new_group.id)))
    #         token = account_activation_token.make_token(user)
    #
    #         email_kwargs = {"user": user.first_name,
    #                         "coded_user": coded_user,
    #                         'coded_group': coded_group,
    #                         "token": token,
    #                         "group_name": target_group,
    #                         "destination": user.email,
    #                         "subject": "Confirm your registration"}
    #         send_result = email_confirmation(user.pk, **email_kwargs)
    #         return redirect('account_activation_sent')
    #
    #     else:
    #         context = {'form': form,
    #                    'title': title}
    #         return render(request, "login_form.html", context)
    # else:
    #     logging.getLogger("info_logger").info(f'Registration disabled')
    #     return render(request, "temp_register.html", {})


def logout_view(request):
    logging.getLogger("info_logger").info(f'logging out {request.user}')
    logout(request)
    return render(request, "home.html", {})


def home_view(request):
    return render(request, "home.html", {})


# def temp_register_view(request):
#     return render(request, "temp_register.html", {})

