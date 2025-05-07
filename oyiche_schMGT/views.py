from oyiche_schMGT.imports import *

# Create your views here.

def get_school(request):
    school = None

    try:

        if str(request.user.userType) == 'superuser':
            return None

        admin = SchoolAdminInformation.objects.get(user=request.user)
        school = SchoolInformation.objects.get(sch_id=admin.school.sch_id)

    except SchoolAdminInformation.DoesNotExist:
        try:
            school = SchoolInformation.objects.get(principal_id=request.user)
        except SchoolInformation.DoesNotExist:
            try:
                student_info = StudentInformation.objects.get(user=request.user.user_id).school.sch_id
                school = SchoolInformation.objects.get(sch_id=student_info)
            except (StudentInformation.DoesNotExist, SchoolInformation.DoesNotExist):
                messages.error(request, "School profile not found! Therefore, school details can't be retrieved.")
                return None  # Explicitly return None on failure

    except SchoolInformation.DoesNotExist:
        messages.error(request, "School profile not found! Therefore, school details can't be retrieved.")
        return None

    return school

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class EditStudentPageView(LoginRequiredMixin, View):
    template_name = "backend/student/edit_student.html"

    user_form = EditUserForm
    info_form = StudentInformationForm

    @method_decorator(has_updated)
    def get(self, request, user_id):

        school = get_school(request)

        query_params = {
            'student_class': request.GET.get("student_class"),
        }

        url = f"{reverse('sch:students')}?{urlencode(query_params)}"

        try:
            school_academic_session = AcademicSession.objects.get(school_info=school, is_current=True)
            school_academic_term = AcademicTerm.objects.get(school_info=school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")

            query_params['academic_session'] = school_academic_session
            query_params['academic_term'] = school_academic_term
            query_params['academic_status'] = academic_status

            user = User.objects.get(user_id=user_id)
            student_info = StudentInformation.objects.get(user=user)

            context = {
                'user_form': self.user_form(instance=user),
                'info_form': self.info_form(instance=student_info),
                'student_class': query_params['student_class'],
                'academic_session': query_params['academic_session'],
                'academic_status': query_params['academic_status']
            }

            return render(request=request, template_name=self.template_name, context=context)
        except User.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
            return redirect(url)
        except StudentInformation.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
            return redirect(url)

    @method_decorator(has_updated)
    def post(self, request, user_id):

        school = get_school(request)

        user = User.objects.get(user_id=user_id)
        student_info = StudentInformation.objects.get(user=user)

        user_form = self.user_form(
            instance=user, data=request.POST, files=request.FILES)
        info_form = self.info_form(instance=student_info, data=request.POST)

        try:
            school_academic_term = AcademicTerm.objects.get(school_info=school, is_current=True)
            school_academic_session = AcademicSession.objects.get(school_info=school, is_current=True)
            academic_status = AcademicStatus.objects.get(status="active")

            query_params = {
                'student_class': request.POST.get("student_class"),
            }

            context = {
                'user_form': user_form,
                'info_form': info_form,
                'student_class': query_params['student_class'],
            }

            if user_form.is_valid() and info_form.is_valid():

                user_form.save()
                info_form.save()

                messages.success(
                    request=request, message="Student Record Updated!!")

                url = f"{reverse('sch:students')}?{urlencode(query_params)}"
                return redirect(url)

            else:

                messages.error(request=request, message="Fix Form Errors!!")
                return render(request=request, template_name=self.template_name, context=context)
        except User.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
        except StudentInformation.DoesNotExist:
            messages.error(request=request,
                           message="Error getting student, Try Again!!")
        except AcademicSession.DoesNotExist:
            messages.error(request, "Academic Session not Found!!")
        except AcademicTerm.DoesNotExist:
            messages.error(request, "Academic Term not found!!")
        except AcademicStatus.DoesNotExist:
            messages.error(request, "Academic Status not found!!")
        return redirect(reverse('sch:students'))

        url = f"{reverse('sch:students')}?{urlencode(query_params)}"
        return redirect(url)

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SchoolFileUploadView(LoginRequiredMixin, ListView):

    school = None
    template_name = "backend/school/file_manager.html"

    def get_queryset(self):
        self.school = get_school(self.request)
        if self.school:
            return FilesManager.objects.filter(school=self.school).order_by('-date_created')
        return FilesManager.objects.none()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SchoolFileUploadView, self).get_context_data(**kwargs)
        form = FilesManagerForm(school=self.school)

        # Files Templates for download
        context['with_studentID'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="with studentID"))
        context['without_studentID'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="without studentID"))
        context['fees_template'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="Fees"))
        context['grading'] = get_object_or_404(
            FilesTemplates, template_type=FileTemplateType.objects.get(template_title="grading"))
        # Page Form
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):

        self.object_list = self.get_queryset()
        form = FilesManagerForm(data=self.request.POST,
                                files=self.request.FILES, school=self.school)

        if form.is_valid():
            data = form.save(commit=False)

            school = get_school(self.request)
            if school:
                data.school = school
                data.save()
                messages.success(request, "File uploaded successfully")
            else:
                messages.error(request, "School profile not found!!")

        else:
            messages.error(request, form.errors.as_text())

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class BatchCreateView(LoginRequiredMixin, View):
    def post(self, request, file_id):
        try:
            uploaded_file = FilesManager.objects.get(pk=file_id)

            if not uploaded_file.used:
                Creation.create(uploaded_file, get_school(self.request))

                uploaded_file.processing_status = "Processing File!"
                uploaded_file.used = True
                uploaded_file.save()
                messages.success(
                    self.request, "File is been processed check details!!")

            else:
                messages.error(self.request, "File has been Used Already!!")

        except FilesManager.DoesNotExist:
            messages.error(self.request, "File Not Found!!")
        finally:
            return redirect('sch:file_manager')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class DeleteFileView(LoginRequiredMixin, View):
    def post(self, request, file_id):
        try:
            uploaded_file = FilesManager.objects.get(pk=file_id)
            uploaded_file.delete()
            messages.success(self.request, "File has been Deleted!!")
        except FilesManager.DoesNotExist:
            messages.error(self.request, "File Not Found!!")
        finally:
            return redirect('sch:file_manager')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SchoolClassesView(LoginRequiredMixin, ListView):

    model = SchoolClasses
    template_name = "backend/classes/school_classes.html"
    form = SchoolClassesForm

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolClasses.objects.filter(school_info=school).order_by('-date_created')
        return SchoolClasses.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolClassesView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school)

        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info

        if 'create' in request.POST:

            form = self.form(request.POST, school=school)
            self.object_list = self.get_queryset()

            if form.is_valid():
                data = form.save(commit=False)
                data.school_info = school

                class_name = form.cleaned_data.get('class_name')

                data.save()
                messages.success(request, f"{class_name} successfully created")
                return redirect("sch:school_classes")

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            class_id = request.POST.get('class_id')

            try:
                SchoolClasses.objects.get(school_info=school, pk=class_id).delete()
                messages.success(
                    request, "Class has been deleted successfully!!")
            except SchoolClasses.DoesNotExist:
                messages.error(request, "Failed to delete class!!")

            return redirect('sch:school_classes')

        elif 'edit' in request.POST:

            class_id = request.POST.get('class_id')
            class_name = request.POST.get('class_name')


            try:
                school_class = SchoolClasses.objects.get(school_info=school, pk=class_id)
                school_class.class_name = class_name
                school_class.save()

                messages.success(
                    request, "Class has been updated successfully!!")
            except SchoolClasses.DoesNotExist:
                messages.error(request, "Failed to update class!!")
            except IntegrityError:
                messages.error(
                    request, f"Failed to update class: Class name '{class_name}' already exists!"
                )

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            return redirect('sch:school_classes')

        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect('sch:school_classes')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SchoolSubjectView(LoginRequiredMixin, ListView):

    model = SchoolSubject
    template_name = "backend/classes/school_subject.html"
    form = SchoolSubjectForm

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolSubject.objects.filter(school_info=school).order_by('-date_created')
        return SchoolSubject.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolSubjectView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school)

        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info

        if 'create' in request.POST:

            form = self.form(request.POST, school=school)
            self.object_list = self.get_queryset()

            if form.is_valid():
                data = form.save(commit=False)
                data.school_info = school

                subject_name = form.cleaned_data.get('subject_name')

                data.save()
                messages.success(request, f"{subject_name} successfully created")
                return redirect("sch:school_subject")

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            subject_id = request.POST.get('subject_id')

            try:
                SchoolSubject.objects.get(school_info=school, pk=subject_id).delete()
                messages.success(
                    request, "Subject has been deleted successfully!!")
            except SchoolSubject.DoesNotExist:
                messages.error(request, "Failed to delete subject!!")

            return redirect('sch:school_subject')

        elif 'edit' in request.POST:

            subject_id = request.POST.get('subject_id')
            subject_name = request.POST.get('subject_name')


            try:
                school_subject = SchoolSubject.objects.get(school_info=school, pk=subject_id)
                school_subject.subject_name = subject_name
                school_subject.save()

                messages.success(
                    request, "Subject has been updated successfully!!")
            except SchoolSubject.DoesNotExist:
                messages.error(request, "Failed to update subject!!")
            except IntegrityError:
                messages.error(
                    request, f"Failed to update subject: Subject name '{school_subject.subject_name}' already exists!"
                )

            except Exception as e:
                messages.error(request, f"An unexpected error occurred: {str(e)}")

            return redirect('sch:school_subject')

        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect('sch:school_subject')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SubjectClassView(LoginRequiredMixin, ListView):

    model = SchoolClassSubjects
    template_name = "backend/classes/subject_class.html"
    form = SchoolClassSubjectForm

    def get_queryset(self, **kwargs):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')
        if school:
            return SchoolClassSubjects.objects.filter(school_info=school, school_class=class_id).order_by('-date_created')
        return SchoolClassSubjects.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')
        context = super(SubjectClassView, self).get_context_data(**kwargs)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        context['form'] = self.form(school=school, school_class=class_id)
        context['class_name'] = class_name.class_name
        context['class_id'] = class_name.pk

        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info
        class_id = self.kwargs.get('class_id')

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        if 'create' in request.POST:

            form = self.form(request.POST, school=school, school_class=class_id)

            self.object_list = self.get_queryset()

            if form.is_valid():
                data = form.save(commit=False)
                data.school_info = school
                data.school_class = class_name

                subject_name = form.cleaned_data.get('school_subject').subject_name

                data.save()
                messages.success(request, f"{subject_name.title()} has been assigned to {class_name.class_name.upper()}!")
                return redirect("sch:subject_class", class_id)

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        elif 'delete' in request.POST:

            subject_id = request.POST.get('subject_id')

            try:
                school_subject = SchoolClassSubjects.objects.get(school_info=school, pk=subject_id)
                school_subject.delete()
                messages.success(
                    request, f"{school_subject.school_subject.subject_name.title()} has been removed from {class_name.class_name.upper()} successfully!")
            except SchoolClassSubjects.DoesNotExist:
                messages.error(request, "Failed to delete subject!")

            return redirect("sch:subject_class", class_id)


        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect("sch:subject_class", class_id)

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SchoolGradesView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):

    model = SchoolGrades
    template_name = "backend/grades/school_grades.html"
    form = SchoolGradeForm

    def get_context_data(self, **kwargs):
        school = get_school(self.request)

        context = super(SchoolGradesView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school)

        return context

    def post(self, request):

        school = get_school(request=request) #Get school info

        form = SchoolGradeForm(request.POST, school=school)

        if form.is_valid():
            data = form.save(commit=False)
            data.school_info = school
            data.save()
            grade_letter = form.cleaned_data.get('grade_letter')
            messages.success(request, f"Grade: {grade_letter} successfully created!!")
            return redirect("sch:school_grade")
        else:
            # If form is invalid, re-render the page with errors
            messages.error(request, form.errors.as_text())
            return render(request=request, template_name=self.template_name, context={'form':form, 'school':school})

        return redirect("sch:school_grade")

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ListGradesView(LoginRequiredMixin, ListView):
    model = SchoolGrades
    template_name = "backend/grades/partials/grade_list.html"

    def get_queryset(self):
        school = get_school(self.request)
        if school:
            return SchoolGrades.objects.filter(school_info=school).order_by('-date_created')
        return SchoolGrades.objects.none()

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class GradesEditView(LoginRequiredMixin, View):

    def get(self, request, grade_id):
        school = get_school(request)

        try:
            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            grade_form = SchoolGradeEditForm(instance=grade, school=school)

            return render(request=request, template_name="backend/grades/partials/grade_form.html", context={'form': grade_form, 'object': grade})

        except SchoolGrades.DoesNotExist:
            return JsonResponse({'error': 'Student Score not found!'}, status=404)

    def post(self, request, grade_id):

        school = get_school(request=request) #Get school info

        try:

            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            form = SchoolGradeEditForm(request.POST, instance=grade, school=school)

            if form.is_valid():
                form.save()
                grade_letter = form.cleaned_data.get('grade_letter')
                messages.success(request, f"Grade: {grade_letter} successfully edited!!")

            else:
                # If form is invalid, re-render the page with errors
                messages.error(request, form.errors.as_text())

        except SchoolGrades.DoesNotExist:
            messages.error(request, "Failed to edit grade!!")
        finally:
            return HttpResponse(status=204, headers={'Hx-Trigger':'listChanged'})

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class GradesDeleteView(LoginRequiredMixin, View):

    def get(self, request, grade_id):
        school = get_school(request)

        try:
            grade = SchoolGrades.objects.get(school_info=school, pk=grade_id)
            grade_form = SchoolGradeEditForm(instance=grade, school=school)

            return render(request=request, template_name="backend/grades/partials/grade_delete.html", context={'form': grade_form, 'object': grade})

        except SchoolGrades.DoesNotExist:

            messages.error(request, "Grade not found!!")
            return redirect('sch:school_grade')

    def post(self, request, grade_id):

        school = get_school(request=request) #Get school info

        try:
            SchoolGrades.objects.get(school_info=school, pk=grade_id).delete()
            messages.success(
                request, "Grade has been deleted successfully!!")
        except SchoolGrades.DoesNotExist:
            messages.error(request, "Failed to delete grade!!")

        return HttpResponse(status=204, headers={'Hx-Trigger':' listChanged'})

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class SchoolClassOptions(LoginRequiredMixin, View):
    template_name = "backend/classes/school_options.html"

    @method_decorator(has_updated)
    def get(self, request, class_id):
        school = get_school(request)

        try:
            class_id = SchoolClasses.objects.get(pk=class_id, school_info=school)
            return render(request=request, template_name=self.template_name, context={'school': school, 'object':class_id})
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ManageStudentSubjectGrades(LoginRequiredMixin, View):

    template_name = "backend/grades/manage_student_grades.html"
    form = UploadStudentSubjectGradeForm
    form2 = StudentScoreGradeForm
    form3 = GetStudentSubjectGradeForm

    # Context variables
    object_list = None
    grade_list = None
    all_student = ''
    add_student = ''
    manage_all = ''

    @method_decorator(has_updated)
    def get(self, request, class_id, subject_id=None):

        self.manage_all = 'active'
        self.all_student = ''
        self.add_student = ''

        self.school = get_school(request)
        self.form = self.form(school=self.school, school_class=class_id)
        self.form2 = self.form2(school=self.school, school_class=class_id)
        self.form3 = self.form3(school=self.school, school_class=class_id)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=self.school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        if subject_id:
            self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_id, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

            self.grade_list = self.grade_list

        context = {
            'form': self.form,
            'form2': self.form2,
            'form3': self.form3,
            'manage_all': self.manage_all,
            'all_student': self.all_student,
            'add_student': self.add_student,
            'class_name': class_name,
            'grade_list': self.grade_list,
        }

        return render(request, template_name=self.template_name, context=context)

    @method_decorator(has_updated)
    def post(self, request, class_id, subject_id=None):

        self.school = get_school(request)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=self.school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        if subject_id:
            self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_id, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

            self.grade_list = self.grade_list

        if 'upload_grade' in request.POST:

            form = self.form(data=request.POST, files=request.FILES, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'all_student': 'active',
                'manage_all': self.manage_all,
                'add_student': self.add_student,
                'class_name': class_name,
                'object_list': self.object_list,
            }

            if form.is_valid():

                # Prepare for bulk create
                grade_list = []

                # Get uploaded file
                df = pd.read_excel(request.FILES['file'])

                # Get submitted session, term & subject
                session = AcademicSession.objects.get(school_info=self.school, is_current=True)
                term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

                try:

                    subject = SchoolClassSubjects.objects.get(school_subject=request.POST.get('subject_name'), school_info=self.school, school_class=class_id)

                    if not SchoolGrades.objects.filter(school_info=self.school).exists():
                        messages.error(request, "upload Grades first!!")
                        return redirect('sch:school_grade')

                    highest_score = 0
                    lowest_score = float('inf')

                    # Pre-fetch all student data for efficiency
                    student_usernames = df.iloc[:,0].str.upper().tolist()
                    students = StudentInformation.objects.filter(user__username__in=student_usernames)
                    student_map = {student.user.username:student for student in students}

                    # Loop through the data
                    for _, row in df.iterrows():

                        ca1 = row.iloc[2]
                        ca2 = row.iloc[3]
                        ca3 = row.iloc[4]
                        exam = row.iloc[5]

                        username  = row.iloc[0].upper()
                        student = student_map[username]

                        if not student:
                            continue #Skip if student doesn't exist

                        score = StudentScores(
                            first_ca=ca1,
                            second_ca=ca2,
                            third_ca=ca3,
                            exam=exam,
                            student=student,
                            school_info=self.school,
                            session=session,
                            term=term,
                            subject=subject
                        )

                        # Perform calculation in memory
                        score.calculate_grade_and_total_score()
                        score.calculate_highest_and_lowest_score()

                        score.calculate_average()
                        score.calculate_positions()

                        # Update highest and lowest score dynamically
                        highest_score = max(score.total_score, highest_score)
                        lowest_score = min(score.total_score, lowest_score)

                        grade_list.append(score)

                    # Bulk create
                    with transaction.atomic():
                        StudentScores.objects.bulk_create(grade_list)

                    scores = StudentScores.objects.filter(
                        school_info=self.school,
                        session=session,
                        term=term,
                        subject=subject
                    )
                    scores.first().calculate_positions()
                    scores.update(
                        highest_score=highest_score,
                        lowest_score=lowest_score
                    )

                    messages.success(request, "Grades uploaded successfully!!")
                    # Return upload grades
                    self.object_list = StudentScores.objects.filter(school_info=self.school, session=session, term=term, subject=subject).order_by('-average')
                    context['object_list'] = self.object_list

                    return render(request, template_name=self.template_name, context=context)
                except SchoolClassSubjects.DoesNotExist:
                    messages.error(request, "Subject not found!!")

                    return render(request, template_name=self.template_name, context=context)

            else:
                messages.error(request=request, message=form.errors.as_text())

                context['form'] = form

                return render(request, template_name=self.template_name, context=context)

        elif 'single_upload' in request.POST:
            form2 = self.form2(data=request.POST, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'all_student': '',
                'manage_all': '',
                'add_student': 'active',
                'class_name': class_name,
                'object_list': self.object_list,
            }

            if form2.is_valid():
                data = form2.save(commit=False)
                data.school_info = self.school

                try:

                    # Get submitted session, term & subject
                    session = AcademicSession.objects.get(school_info=self.school, is_current=True)
                    term = AcademicTerm.objects.get(school_info=self.school, is_current=True)

                    data.session = session
                    data.term = term

                    data.calculate_grade_and_total_score()
                    data.calculate_average()
                    data.save()
                    data.calculate_highest_and_lowest_score()
                    data.calculate_positions()

                    messages.success(request, "Grade uploaded successfully!!")

                    return render(request, template_name=self.template_name, context=context)

                except AcademicSession.DoesNotExist:
                    messages.error(request, "Academic Session not Found!!")
                except AcademicTerm.DoesNotExist:
                    messages.error(request, "Academic Term not found!!")

                return render(request, template_name=self.template_name, context=context)

            else:

                context['form2'] = form2
                return render(request, template_name=self.template_name, context=context)

        elif 'get_grades' in request.POST:

            form3 = self.form3(data=request.POST, school=self.school, school_class=class_id)

            context = {
                'form': self.form(school=self.school, school_class=class_id),
                'form2': self.form2(school=self.school, school_class=class_id),
                'form3': self.form3(school=self.school, school_class=class_id),
                'manage_all': 'active',
                'all_student': '',
                'add_student': self.add_student,
                'class_name': class_name,
                'object_list': self.object_list,
                'grade_list': self.grade_list,
            }

            if form3.is_valid():
                subject_name = form3.cleaned_data.get('subject_name').school_subject

                self.grade_list = StudentScores.objects.filter(school_info=self.school, subject__school_subject=subject_name, session__is_current=True, term__is_current=True, subject__school_class=class_id).order_by('-average')

                context['grade_list'] = self.grade_list

            else:

                context['form3'] = form3

            return render(request, template_name=self.template_name, context=context)

        messages.error(request=request, message="couldn't handle request, Try again!!")
        context = {
            'form': self.form(school=self.school, school_class=class_id),
            'form2': self.form2(school=self.school, school_class=class_id),
            'form3': self.form3(school=self.school, school_class=class_id),
            'manage_all': 'active',
            'all_student': '',
            'add_student': self.add_student,
            'class_name': class_name,
            'object_list': self.object_list,
        }

        return render(request, template_name=self.template_name, context=context)

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class StudentScoreEditView(LoginRequiredMixin, View):

    @method_decorator(has_updated)
    def get(self, request, score_id):
        school = get_school(request)

        try:
            score = StudentScores.objects.get(school_info=school, pk=score_id)
            score_form = StudentScoreGradeEditForm(instance=score)

            return render(request=request, template_name="backend/grades/partials/score_form.html", context={'form': score_form, 'object': score})

        except StudentScores.DoesNotExist:

            return JsonResponse({'error': 'Student Score not found!'}, status=404)

    @method_decorator(has_updated)
    def post(self, request, score_id):
        school = get_school(request=request) #Get school info

        try:
            score = StudentScores.objects.get(school_info=school, pk=score_id)
            form = StudentScoreGradeEditForm(request.POST, instance=score)

            if form.is_valid():

                data = form.save(commit=False)
                data.calculate_grade_and_total_score()
                data.calculate_average()
                data.save()
                data.calculate_highest_and_lowest_score()
                data.calculate_positions()

                messages.success(request, f"{score.student.student_name}: score has been successfully edited!!")

            else:
                # If form is invalid, re-render the page with errors
                messages.error(request, form.errors.as_text())

            return redirect('sch:manage_student_grades', score.subject.school_class.pk, score.subject.school_subject.pk)

        except SchoolGrades.DoesNotExist:
            messages.error(request, "Student Grade not found Try Again!!")
            return redirect('sch:school_classes')

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class StudentScoreDeleteView(LoginRequiredMixin, SuccessMessageMixin, View):
    login_url = 'auth:login'
    model = StudentScores
    success_message = ""

    @method_decorator(has_updated)
    def post(self, request, pk):

        school = get_school(request=request)
        subject = request.POST['subject']
        class_id = request.POST['class_id']

        try:
            # Delete the score
            score = StudentScores.objects.get(pk=pk, school_info=school)
            score.delete()

            # Success message
            messages.success(request, f"{score.student.student_name} {score.subject.school_subject.subject_name.title()} scores have been deleted successfully!")

            score.calculate_highest_and_lowest_score()
            score.calculate_positions()

            # Redirect to the appropriate URL using the object's details
            return redirect(reverse('sch:manage_student_grades', kwargs={
                'class_id': score.subject.school_class.pk,
                'subject_id': score.subject.school_subject.pk
            }))

        except StudentScores.DoesNotExist:

            messages.error(request, 'Failed to delete student score')

            return redirect(reverse('sch:manage_student_grades', kwargs={
                'class_id': class_id,
                'subject_id': subject
            }))

@method_decorator([is_school_or_admin, has_updated], name='dispatch')
class ComputeResultView(LoginRequiredMixin, ListView):
    template_name = "backend/results/compute_result.html"
    model = StudentPerformance

    def get_queryset(self):
        school = get_school(self.request)
        class_id = self.kwargs.get('class_id')

        if school and class_id:

            # Get all subjects assigned to the class
            subjects = SchoolClassSubjects.objects.filter(
                school_info=school,
                school_class=class_id
            ).values_list('school_subject__subject_name', 'id',)

            # Get student performance with scores for each subject
            queryset = (
                StudentPerformance.objects.filter(
                    school_info=school,
                    current_enrollment__student_class=class_id,
                    current_enrollment__academic_session__is_current=True,
                    current_enrollment__academic_term__is_current=True,
                )
                .select_related('student', 'current_enrollment')
                .prefetch_related(
                    Prefetch(
                        'student__student_scores',
                        queryset=StudentScores.objects.filter(
                            school_info=school,
                            term__is_current=True,
                            session__is_current=True,
                        )
                    )
                )
                .order_by('-student_average')
            )

            return queryset, subjects

        return StudentPerformance.objects.none(), []

    def get_context_data(self, **kwargs):
        class_id = self.kwargs.get('class_id', '')
        school = get_school(self.request)

        context = super().get_context_data(**kwargs)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        queryset, subjects = self.get_queryset()
        context['queryset'] = queryset
        context['subjects'] = subjects
        context['school'] = school
        context["class_name"] = class_name
        context['academic_session'] = AcademicSession.objects.filter(is_current=True, school_info=school).first()
        context['academic_term'] = AcademicTerm.objects.filter(is_current=True, school_info=school).first()

        return context

    @method_decorator(has_updated)
    def post(self, request, class_id):

        # All required variables
        school = get_school(self.request)

        try:
            class_name = SchoolClasses.objects.get(pk=class_id, school_info=school)
        except SchoolClasses.DoesNotExist:
            messages.error(request, "Class not found!!")
            return redirect('sch:school_classes')

        academic_term = AcademicTerm.objects.filter(is_current=True, school_info=school).first()
        academic_session = AcademicSession.objects.filter(is_current=True, school_info=school).first()
        class_detail = class_name

        def perform_computation(which, student_performance_list, required_unit=None, school_unit_info=None):

            # Create performances and calculate student averages
            with transaction.atomic():
                # Bulk create student performances

                if which == 'compute':
                    performances = StudentPerformance.objects.bulk_create(student_performance_list)

                if which == 're-compute':
                    performances = student_performance_list

                # Calculate student averages and other individual data
                for performance in performances:
                    performance.calculate_student_average_total_marks_total_subject()

                # Bulk update all student-related fields
                StudentPerformance.objects.bulk_update(
                    performances,
                    ['total_marks_obtained', 'total_subject', 'student_average']
                )

                # Calculate class averages after all student averages are ready
                for performance in performances:
                    performance.calculate_class_average()
                    performance.calculate_school_remark()

                # Bulk update all class average fields
                StudentPerformance.objects.bulk_update(
                    performances,
                    ['class_average', 'school_remark']
                )

                # Calculate term positions
                first_performance = StudentPerformance.objects.filter(
                    school_info=school,
                    current_enrollment__student_class=class_detail,
                    current_enrollment__academic_term=academic_term,
                    current_enrollment__academic_session=academic_session
                ).first()

                if first_performance: first_performance.calculate_term_position()

                if which == 'compute':
                    
                    # Deduct Units
                    school_unit_info.available_unit -= required_units
                    school_unit_info.save()

                    # Update the unit used for the current term
                    obj, _ = UnitUsedByTerm.objects.get_or_create(
                        school=school,
                        academic_session=academic_session,
                        academic_term=academic_term,
                    )

                    obj.unit_used += required_units
                    obj.save()

        # List to hold the student performance instance for bulk creation
        student_performance_list = []

        # Get all students enrolled in the class
        enrolled_class = StudentEnrollment.objects.filter(
            academic_session=academic_session,
            academic_term=academic_term,
            student_class=class_detail,
            academic_status__status="active",
        )

        # Validate if student exist in the enrolled class
        if not enrolled_class:
            messages.error(request, f"No student enrolled into {class_detail.class_name.upper()} class!!")
            return redirect('sch:compute_results', class_id)

        if 'compute' in request.POST:

            # Create Performance for each student
            student_performance_list = [
                StudentPerformance(
                    school_info=school,
                    student=student.student,
                    current_enrollment=student
                )
                for student in enrolled_class
            ]

            try:

                # Get the current unit balance for the school
                school_unit = SchoolUnit.objects.filter(school=school).first()

                required_units = len(student_performance_list)

                if not school_unit or school_unit.available_unit < required_units:
                    messages.error(request, f"Insufficient units for computation! Required: {required_units}, Available: {school_unit.available_unit if school_unit else 0}")
                    return redirect('sch:compute_results', class_id)

                # Proceed with computation
                perform_computation(which='compute', student_performance_list=student_performance_list, required_unit=required_units, school_unit_info=school_unit)


                messages.success(request=request, message=f'computation successful!')
                return redirect('sch:compute_results', class_id)

            except ValueError as e:
                messages.error(request=request, message=str(e))
                return redirect('sch:compute_results', class_id)


        elif 're-compute' in request.POST:
            # Create Performance for each student
            student_performance_list = StudentPerformance.objects.filter(
                school_info=school,
                current_enrollment__student_class=class_detail,
                current_enrollment__academic_term=academic_term,
                current_enrollment__academic_session=academic_session,
            )

            try:

                perform_computation(which='re-compute', student_performance_list=student_performance_list)

                messages.success(request=request, message=f'computation successful!')
                return redirect('sch:compute_results', class_id)

            except ValueError as e:
                messages.error(request=request, message=str(e))
                return redirect('sch:compute_results', class_id)

        messages.error(request=request, message="Couldn't handle request, Try again!!")
        return redirect('sch:compute_results', class_id)

@method_decorator([is_school], name='dispatch')
class ManageSchoolDetailsView(LoginRequiredMixin, View):

    template_name = "backend/school/manage_school_details.html"

    form = SchoolInformationForm
    form2 = AcademicSessionForm
    form3 = AcademicTermForm

    # Context variables
    object = None
    session_list = None
    term_list = None
    context = {}

    school_details = ''
    school_session = ''
    school_term = ''

    def helper(self, request):

        self.school_details = 'active'
        self.school_session = ''
        self.school_term = ''

        self.school = get_school(request)

        self.object = SchoolInformation.objects.filter(principal_id=request.user).first()
        self.session_list = AcademicSession.objects.filter(school_info=self.school).order_by('-date_created')
        self.term_list = AcademicTerm.objects.filter(school_info=self.school).order_by('-date_created')


        self.context = {

            'form': self.form,
            'form2': self.form2,
            'form3': self.form3,

            'school_details': self.school_details,
            'school_session': self.school_session,
            'school_term': self.school_term,

            'object': self.object,
            'session_list': self.session_list,
            'term_list': self.term_list,
        }

    def get(self, request):

        self.helper(request)

        self.form = self.form(instance=self.object)
        self.context['form'] = self.form

        return render(request, template_name=self.template_name, context=self.context)

    def post(self, request):

        self.helper(request)

        self.context = {

            'form': self.form,
            'form2': self.form2,
            'form3': self.form3,

            'school_details': self.school_details,
            'school_session': self.school_session,
            'school_term': self.school_term,

            'object': self.object,
            'session_list': self.session_list,
            'term_list': self.term_list,
        }

        self.school = get_school(request)
        self.object = SchoolInformation.objects.filter(principal_id=request.user).first()

        if 'update' in request.POST:

            form = SchoolInformationForm(data=request.POST, instance=self.object, files=request.FILES)

            if form.is_valid():

                data = form.save(commit=False)
                data.school_updated = True

                data.save()
                messages.success(request=request, message="School information updated successfully!")

                return redirect('sch:manage_school_details')
            else:
                messages.error(request=request, message=form.errors.as_text())
                self.context['form'] = form

        elif 'create_session' in request.POST:

            self.context['school_session'] = 'active'
            self.context['school_details'] = ''
            self.context['school_term'] = ''

            form2 = self.form2(data=request.POST)

            if form2.is_valid():

                data = form2.save(commit=False)
                data.school_info = self.school

                is_current = data.is_current

                all_academic_session = AcademicSession.objects.filter(school_info=self.school)

                if not all_academic_session.exists():

                    data.is_current = True
                    data.save()

                    messages.success(request=request, message="Academic Session Created!")

                    self.context['session_list'] = AcademicSession.objects.filter(school_info=self.school).order_by('-date_created')

                    return render(request, template_name=self.template_name, context=self.context)

                else:


                    try:

                        with transaction.atomic():

                            if is_current:

                                academic_sessions = AcademicSession.objects.filter(school_info=self.school, is_current=True)

                                for session in academic_sessions:
                                    session.is_current = False
                                    session.is_completed = True

                                AcademicSession.objects.bulk_update(academic_sessions, ['is_current', 'is_completed'])

                            data.save()

                        messages.success(request=request, message="Academic Session Created!")

                        self.context['session_list'] = AcademicSession.objects.filter(school_info=self.school).order_by('-date_created')

                        return render(request, template_name=self.template_name, context=self.context)

                    except IntegrityError:

                        messages.error(request=request, message=f"{data.session} session already exist")

                        self.context['form2'] = form2

            else:

                messages.error(request=request, message=form2.errors.as_text())

        elif 'edit_session' in request.POST:

            self.context['school_session'] = 'active'
            self.context['school_details'] = ''
            self.context['school_term'] = ''

            session_id = request.POST.get('session_id')
            session_name = request.POST.get('session_name')
            session_desc = request.POST.get('session_desc')

            is_current = request.POST.get('is_current') == 'on'

            try:

                data = AcademicSession.objects.get(pk=session_id)
                data.session = session_name
                data.session_description = session_desc

                if is_current:

                    data.is_current = True

                    # Find the existing current session for the same school and unset it
                    academic_session = AcademicSession.objects.filter(school_info=self.school, is_current=True).first()

                    if academic_session and academic_session != data:

                        try:

                            with transaction.atomic():
                                academic_session.is_current = False
                                academic_session.is_completed = True
                                academic_session.save()
                                data.save()
                                messages.success(request, "Session updated successfully.")

                        except IntegrityError:
                            messages.error(request, f"Session '{data.session}' already exists.")
                    else:
                        messages.error(request, f"No specific action taken!!")

                else:

                    # If no session is currently marked as "current", prompt the user
                    academic_session = AcademicSession.objects.filter(school_info=self.school, is_current=True)

                    if not academic_session.exists():
                        messages.error(request, "Please select a current session.")

                        return render(request, template_name=self.template_name, context=self.context)

                    if academic_session.first().pk == data.pk:
                        messages.error(request, "current session cannot be empty, kindly update first!.")

                        return render(request, template_name=self.template_name, context=self.context)

            except AcademicSession.DoesNotExist:
                messages.error(request, "Failed to edit academic session. Try again!")

        elif 'delete_session' in request.POST:

            self.context['school_session'] = 'active'
            self.context['school_details'] = ''
            self.context['school_term'] = ''

            session_id = request.POST.get('session_id')

            try:

                academic_session = AcademicSession.objects.get(school_info=self.school, pk=session_id)

                if academic_session.is_completed:
                    messages.error(request, "Completed session cannot be deleted!!")

                elif not academic_session.is_current and not academic_session.is_completed:
                    academic_session.delete()
                    messages.success(
                        request, "Academic session has been deleted successfully!!")
                else:
                    messages.error(
                        request, "Current academic session or completed session cannnot be deleted!!")

            except AcademicSession.DoesNotExist:
                messages.error(request, "Failed to delete session!!")

        elif 'edit_term' in request.POST:

            self.context['school_session'] = ''
            self.context['school_details'] = ''
            self.context['school_term'] = 'active'

            term_id = request.POST.get('term_id')
            term_name = request.POST.get('term_name')
            term_desc = request.POST.get('term_desc')

            is_current = request.POST.get('is_current') == 'on'

            try:

                data = AcademicTerm.objects.get(pk=term_id)
                data.term = term_name
                data.term_description = term_desc

                if is_current:
                    data.is_current = True

                    # Find the existing current session for the same school and unset it
                    academic_term = AcademicTerm.objects.filter(school_info=self.school, is_current=True).first()
                    if academic_term and academic_term != data:
                        academic_term.is_current = False
                        academic_term.save()

                else:
                    # If no term is currently marked as "current", prompt the user
                    academic_term = AcademicTerm.objects.filter(school_info=self.school, is_current=True)

                    if not academic_term.exists():
                        messages.error(request, "Please select a current term.")

                        return render(request, template_name=self.template_name, context=self.context)

                    if academic_term.first().pk == data.pk:
                        messages.error(request, "current term cannot be empty, kindly update!.")

                        return render(request, template_name=self.template_name, context=self.context)

                try:
                    data.save()
                    messages.success(request, "Term updated successfully.")

                except IntegrityError:
                    messages.error(request, f"Term '{data.term}' already exists.")

            except AcademicTerm.DoesNotExist:
                messages.error(request, "Failed to edit academic term. Try again!")

        return render(request, template_name=self.template_name, context=self.context)

class StudentResultView(LoginRequiredMixin, ListView):

    model = StudentPerformance
    template_name = "backend/results/student_result.html"
    form = StudentPerformanceForm

    def get_queryset(self):
        school = get_school(self.request)
        try:
            student = StudentInformation.objects.get(user=self.request.user)
            if school:
                return StudentPerformance.objects.filter(school_info=school, student=student, current_enrollment__has_paid=True).select_related('current_enrollment').order_by('-date_created')[:5]

        except StudentInformation.DoesNotExist:
            messages.error(request, "Student record not found!!")
        return StudentPerformance.objects.none()

    def get_context_data(self, **kwargs):
        school = get_school(self.request)
        user = self.request.user #Get student info
        student_profile = StudentInformation.objects.filter(user=user).first()

        context = super(StudentResultView, self).get_context_data(**kwargs)

        context['form'] = self.form(school=school, student=student_profile)
        context['queryset'] = self.get_queryset()
        context['school'] = school

        return context

    def post(self, request, *args, **kwargs):

        school = get_school(request=request) #Get school info
        user = self.request.user #Get student info
        student_profile = StudentInformation.objects.filter(user=user).first()

        if 'get_result' in request.POST:

            form = self.form(request.POST, school=school, student=student_profile)
            self.object_list = self.get_queryset()

            if form.is_valid():

                student_class = form.cleaned_data.get('student_class')
                academic_session = form.cleaned_data.get('academic_session')
                academic_term = form.cleaned_data.get('academic_term')

                queryset = StudentPerformance.objects.filter(
                    school_info=school,
                    student=student_profile,
                    current_enrollment__student_class=student_class,
                    current_enrollment__academic_term=academic_term,
                    current_enrollment__academic_session=academic_session,
                    current_enrollment__has_paid=True,
                ).select_related('current_enrollment')

                return render(
                    request=request,
                    template_name=self.template_name,
                    context={
                        'form': form,
                        'queryset': queryset,
                        'school': school,
                    }
                )

            else:
                # If form is invalid, re-render the page with errors
                context = self.get_context_data()
                context['form'] = form
                messages.error(request, form.errors.as_text())
                return self.render_to_response(context)

        else:
            messages.error(request=request,
                           message="couldn't handle request, Try again!!")
            return redirect('sch:student_result')

class ResultPreviewPage(LoginRequiredMixin, View):

    def get(self, request, performance_id):
        school = get_school(request)

        try:

            if school:

                # Fetch performance first
                performance = StudentPerformance.objects.select_related('student', 'current_enrollment').get(
                    school_info=school, pk=performance_id
                )

                # Fetch related student scores separately
                student_scores = StudentScores.objects.filter(
                    school_info=school,
                    student=performance.student,
                    term=performance.current_enrollment.academic_term,
                    session=performance.current_enrollment.academic_session,
                )

                return render(request=request, template_name="backend/results/partials/inner_result_student.html", context={'object': performance, 'school':school, 'scores':student_scores})

            return JsonResponse({'error': 'School not found!'}, status=404)

        except StudentPerformance.DoesNotExist:
            return JsonResponse({'error': 'Student result not found!'}, status=404)

@method_decorator([is_school_or_admin], name='dispatch')
class ManageSchoolResultView(LoginRequiredMixin, View):

    template_name = "backend/remarks/manage_school_remarks.html"

    form = SchoolRemarkForm

    # Context variables
    teacher_list = None
    context = {}


    def helper(self, request):

        self.school = get_school(request)

        self.teacher_list = SchoolRemark.objects.filter(school_info=self.school).order_by('-date_created')

        self.context = {

            'form': self.form,
            'teacher_list': self.teacher_list,

        }

    def get(self, request):

        self.helper(request)

        return render(request, template_name=self.template_name, context=self.context)

    def post(self, request):

        self.helper(request)

        self.context = {

            'form': self.form,

            'teacher_list': self.teacher_list,

        }

        self.school = get_school(request)

        if 'create_remark' in request.POST:

            form = self.form(data=request.POST, school=self.school)

            if form.is_valid():

                data = form.save(commit=False)
                data.school_info = self.school
                data.save()

                messages.success(request=request, message="Teacher Remark has been saved!")

                self.context['teacher_list'] = SchoolRemark.objects.filter(school_info=self.school).order_by('-date_created')

                return render(request, template_name=self.template_name, context=self.context)

            else:
                self.context['form'] = form
                messages.error(request=request, message=form.errors.as_text())

        elif 'edit_remark' in request.POST:

            remark_id = request.POST.get('remark_id')
            min_average = request.POST.get('min_average')
            max_average = request.POST.get('max_average')
            teacher_remark = request.POST.get('teacher_remark')
            principal_remark = request.POST.get('principal_remark')

            try:

                data = SchoolRemark.objects.get(pk=remark_id)

                # Convert to float
                min_avg = float(min_average)
                max_avg = float(max_average)

                # Validate min and max average
                if min_avg > max_avg:
                    messages.error(request, "Minimum average cannot be greater than Maximum average.")
                    return redirect(request.META.get('HTTP_REFERER', 'default_view')) # Redirect

                # Check for overlapping remark range excluding the current remark being edited

                overlapping_remark = SchoolRemark.objects.filter(
                    school_info=data.school_info
                ).exclude(pk=remark_id).filter(
                    Q(min_average__lte=max_avg, max_average__gte=min_avg)
                ).exists()

                if overlapping_remark:
                    messages.error(request, "A School Remark with the provided range already exists.")
                    return redirect(request.META.get('HTTP_REFERER', 'default_view'))

                data.min_average = min_average
                data.max_average = max_average
                data.teacher_remark = teacher_remark
                data.principal_remark = principal_remark

                data.save()
                messages.success(request, "Remark updated successfully.")

            except SchoolRemark.DoesNotExist:
                messages.error(request, "Failed to edit remark. Try again!")

        elif 'delete_remark' in request.POST:

            remark_id = request.POST.get('remark_id')

            try:

                remark = SchoolRemark.objects.get(school_info=self.school, pk=remark_id)
                messages.success(request, 'Remark has been deleted successfully!!')
                remark.delete()

            except SchoolRemark.DoesNotExist:
                messages.error(request, "Failed to delete remark!!")

        return render(request, template_name=self.template_name, context=self.context)
