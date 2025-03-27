from django import forms
from .models import Submission


class SubmissionForm(forms.ModelForm):
    """
    แบบฟอร์มสำหรับการส่งไฟล์งาน

    ใช้สำหรับอัปโหลดไฟล์งานของโครงงานพร้อมชื่อไฟล์
    """

    class Meta:
        model = Submission # โมเดลที่เชื่อมโยง
        fields = ['file_name', 'file'] # ฟิลด์ที่แสดงในฟอร์ม

        # กำหนดป้ายกำกับฟิลด์เป็นภาษาไทย
        labels = {
            'file_name': 'ชื่อไฟล์',
            'file': 'เลือกไฟล์'
        }

        # กำหนด widget และ attribute ของ HTML
        widgets = {
            'file_name': forms.TextInput(attrs={'class': 'form-control'}),
            'file': forms.FileInput(attrs={'class': 'form-control'})
        }
