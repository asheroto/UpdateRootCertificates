<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()>
Partial Class MainWindow
    Inherits System.Windows.Forms.Form

    'Form overrides dispose to clean up the component list.
    <System.Diagnostics.DebuggerNonUserCode()>
    Protected Overrides Sub Dispose(ByVal disposing As Boolean)
        Try
            If disposing AndAlso components IsNot Nothing Then
                components.Dispose()
            End If
        Finally
            MyBase.Dispose(disposing)
        End Try
    End Sub

    'Required by the Windows Form Designer
    Private components As System.ComponentModel.IContainer

    'NOTE: The following procedure is required by the Windows Form Designer
    'It can be modified using the Windows Form Designer.  
    'Do not modify it using the code editor.
    <System.Diagnostics.DebuggerStepThrough()>
    Private Sub InitializeComponent()
        Me.components = New System.ComponentModel.Container()
        Dim resources As System.ComponentModel.ComponentResourceManager = New System.ComponentModel.ComponentResourceManager(GetType(MainWindow))
        Me.Button_Go = New System.Windows.Forms.Button()
        Me.Label1 = New System.Windows.Forms.Label()
        Me.Label2 = New System.Windows.Forms.Label()
        Me.Label_RootCertCabs = New System.Windows.Forms.LinkLabel()
        Me.Label_DisallowedCertsCab = New System.Windows.Forms.LinkLabel()
        Me.Label3 = New System.Windows.Forms.Label()
        Me.Label4 = New System.Windows.Forms.Label()
        Me.Timer_AppUpdate = New System.Windows.Forms.Timer(Me.components)
        Me.BackgroundWorker_AppUpdate = New System.ComponentModel.BackgroundWorker()
        Me.ThirdPartyLicenseInfo = New System.Windows.Forms.LinkLabel()
        Me.MoreInfoCTL = New System.Windows.Forms.LinkLabel()
        Me.Label_TempPath = New System.Windows.Forms.LinkLabel()
        Me.Label_ReportIssue = New System.Windows.Forms.LinkLabel()
        Me.SuspendLayout()
        '
        'Button_Go
        '
        Me.Button_Go.BackColor = System.Drawing.Color.White
        Me.Button_Go.Location = New System.Drawing.Point(15, 294)
        Me.Button_Go.Name = "Button_Go"
        Me.Button_Go.Size = New System.Drawing.Size(606, 79)
        Me.Button_Go.TabIndex = 0
        Me.Button_Go.Text = "Sound good? Click here to download and install the latest root certs!"
        Me.Button_Go.UseVisualStyleBackColor = False
        '
        'Label1
        '
        Me.Label1.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Bold, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label1.Location = New System.Drawing.Point(12, 6)
        Me.Label1.Name = "Label1"
        Me.Label1.Size = New System.Drawing.Size(610, 23)
        Me.Label1.TabIndex = 1
        Me.Label1.Text = "How this program works:"
        Me.Label1.TextAlign = System.Drawing.ContentAlignment.MiddleCenter
        '
        'Label2
        '
        Me.Label2.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label2.Location = New System.Drawing.Point(12, 32)
        Me.Label2.Name = "Label2"
        Me.Label2.Size = New System.Drawing.Size(610, 261)
        Me.Label2.TabIndex = 2
        Me.Label2.Text = resources.GetString("Label2.Text")
        '
        'Label_RootCertCabs
        '
        Me.Label_RootCertCabs.AutoSize = True
        Me.Label_RootCertCabs.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label_RootCertCabs.Location = New System.Drawing.Point(24, 52)
        Me.Label_RootCertCabs.Name = "Label_RootCertCabs"
        Me.Label_RootCertCabs.Size = New System.Drawing.Size(531, 17)
        Me.Label_RootCertCabs.TabIndex = 3
        Me.Label_RootCertCabs.TabStop = True
        Me.Label_RootCertCabs.Text = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authrootst" &
    "l.cab"
        '
        'Label_DisallowedCertsCab
        '
        Me.Label_DisallowedCertsCab.AutoSize = True
        Me.Label_DisallowedCertsCab.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label_DisallowedCertsCab.Location = New System.Drawing.Point(24, 107)
        Me.Label_DisallowedCertsCab.Name = "Label_DisallowedCertsCab"
        Me.Label_DisallowedCertsCab.Size = New System.Drawing.Size(565, 17)
        Me.Label_DisallowedCertsCab.TabIndex = 4
        Me.Label_DisallowedCertsCab.TabStop = True
        Me.Label_DisallowedCertsCab.Text = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/disallowed" &
    "certstl.cab"
        '
        'Label3
        '
        Me.Label3.AutoSize = True
        Me.Label3.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label3.Location = New System.Drawing.Point(24, 160)
        Me.Label3.Name = "Label3"
        Me.Label3.Size = New System.Drawing.Size(190, 17)
        Me.Label3.TabIndex = 5
        Me.Label3.Text = "Temp Path (for cab && log files):"
        '
        'Label4
        '
        Me.Label4.AutoSize = True
        Me.Label4.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label4.Location = New System.Drawing.Point(24, 210)
        Me.Label4.Name = "Label4"
        Me.Label4.Size = New System.Drawing.Size(292, 34)
        Me.Label4.TabIndex = 7
        Me.Label4.Text = "certutil -addstore -f root authroot.stl" & Global.Microsoft.VisualBasic.ChrW(13) & Global.Microsoft.VisualBasic.ChrW(10) & "certutil -addstore -f disallowed disallo" &
    "wedcert.stl"
        '
        'Timer_AppUpdate
        '
        Me.Timer_AppUpdate.Interval = 1000
        '
        'BackgroundWorker_AppUpdate
        '
        '
        'ThirdPartyLicenseInfo
        '
        Me.ThirdPartyLicenseInfo.AutoSize = True
        Me.ThirdPartyLicenseInfo.Font = New System.Drawing.Font("Segoe UI", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.ThirdPartyLicenseInfo.Location = New System.Drawing.Point(553, 376)
        Me.ThirdPartyLicenseInfo.Name = "ThirdPartyLicenseInfo"
        Me.ThirdPartyLicenseInfo.Size = New System.Drawing.Size(68, 13)
        Me.ThirdPartyLicenseInfo.TabIndex = 8
        Me.ThirdPartyLicenseInfo.TabStop = True
        Me.ThirdPartyLicenseInfo.Text = "License Info"
        '
        'MoreInfoCTL
        '
        Me.MoreInfoCTL.AutoSize = True
        Me.MoreInfoCTL.Font = New System.Drawing.Font("Segoe UI", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.MoreInfoCTL.Location = New System.Drawing.Point(12, 378)
        Me.MoreInfoCTL.Name = "MoreInfoCTL"
        Me.MoreInfoCTL.Size = New System.Drawing.Size(146, 13)
        Me.MoreInfoCTL.TabIndex = 9
        Me.MoreInfoCTL.TabStop = True
        Me.MoreInfoCTL.Text = "About Certificate Trust Lists"
        '
        'Label_TempPath
        '
        Me.Label_TempPath.Font = New System.Drawing.Font("Segoe UI", 9.75!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label_TempPath.Location = New System.Drawing.Point(220, 160)
        Me.Label_TempPath.Name = "Label_TempPath"
        Me.Label_TempPath.Size = New System.Drawing.Size(400, 17)
        Me.Label_TempPath.TabIndex = 10
        Me.Label_TempPath.TabStop = True
        Me.Label_TempPath.Text = "Temp Path"
        '
        'Label_ReportIssue
        '
        Me.Label_ReportIssue.AutoSize = True
        Me.Label_ReportIssue.Font = New System.Drawing.Font("Segoe UI", 8.25!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.Label_ReportIssue.Location = New System.Drawing.Point(282, 378)
        Me.Label_ReportIssue.Name = "Label_ReportIssue"
        Me.Label_ReportIssue.Size = New System.Drawing.Size(71, 13)
        Me.Label_ReportIssue.TabIndex = 11
        Me.Label_ReportIssue.TabStop = True
        Me.Label_ReportIssue.Text = "Report Issue"
        '
        'MainWindow
        '
        Me.AutoScaleDimensions = New System.Drawing.SizeF(9.0!, 21.0!)
        Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
        Me.BackColor = System.Drawing.Color.White
        Me.ClientSize = New System.Drawing.Size(634, 398)
        Me.Controls.Add(Me.Label_ReportIssue)
        Me.Controls.Add(Me.Label_TempPath)
        Me.Controls.Add(Me.MoreInfoCTL)
        Me.Controls.Add(Me.ThirdPartyLicenseInfo)
        Me.Controls.Add(Me.Label4)
        Me.Controls.Add(Me.Label3)
        Me.Controls.Add(Me.Label_DisallowedCertsCab)
        Me.Controls.Add(Me.Label_RootCertCabs)
        Me.Controls.Add(Me.Label2)
        Me.Controls.Add(Me.Label1)
        Me.Controls.Add(Me.Button_Go)
        Me.Font = New System.Drawing.Font("Segoe UI", 12.0!, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, CType(0, Byte))
        Me.FormBorderStyle = System.Windows.Forms.FormBorderStyle.FixedSingle
        Me.Icon = CType(resources.GetObject("$this.Icon"), System.Drawing.Icon)
        Me.Margin = New System.Windows.Forms.Padding(4, 5, 4, 5)
        Me.MaximizeBox = False
        Me.Name = "MainWindow"
        Me.StartPosition = System.Windows.Forms.FormStartPosition.CenterScreen
        Me.Text = "Update Root Certificates"
        Me.ResumeLayout(False)
        Me.PerformLayout()

    End Sub

    Friend WithEvents Button_Go As Button
    Friend WithEvents Label1 As Label
    Friend WithEvents Label2 As Label
    Friend WithEvents Label_RootCertCabs As LinkLabel
    Friend WithEvents Label_DisallowedCertsCab As LinkLabel
    Friend WithEvents Label3 As Label
    Friend WithEvents Label4 As Label
    Friend WithEvents Timer_AppUpdate As Timer
    Friend WithEvents BackgroundWorker_AppUpdate As System.ComponentModel.BackgroundWorker
    Friend WithEvents ThirdPartyLicenseInfo As LinkLabel
    Friend WithEvents MoreInfoCTL As LinkLabel
    Friend WithEvents Label_TempPath As LinkLabel
    Friend WithEvents Label_ReportIssue As LinkLabel
End Class
