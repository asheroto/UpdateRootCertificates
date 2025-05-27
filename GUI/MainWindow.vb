Imports System.ComponentModel
Imports System.IO
Imports System.Net
Imports Newtonsoft.Json.Linq

Friend Class MainWindow

    'If enabled, will not delete the temp folder
    Friend Shared NoCleanup As Boolean = False

    'Initially set to nothing, but will be set to a random folder in the temp directory in Form_Load
    Friend Shared TempPath As String = Nothing

    Private Sub Main_Load(sender As Object, e As EventArgs) Handles MyBase.Load
        'Put arguments -h, /h, --help, -help, /help, into an array
        Dim args() As String = {"-h", "/h", "--help", "-help", "/help", "/?"}
        'If any of the arguments are found, show the help dialog
        If Environment.GetCommandLineArgs.Intersect(args, StringComparer.OrdinalIgnoreCase).Any Then
            MessageBox.Show("UpdateRootCertificates" + vbNewLine + vbNewLine + "Usage: UpdateRootCertificates.exe [-NoCleanup]" + vbNewLine + vbNewLine + "Example: UpdateRootCertificates.exe -NoCleanup" + vbNewLine + vbNewLine + "The -NoCleanup argument will keep the temp folder containing the files and logs. This is useful for debugging purposes.", "Help", MessageBoxButtons.OK, MessageBoxIcon.Information)
            Environment.Exit(0)
        End If

        'If the -NoCleanup argument is passed (case-insensitive), we'll keep the temp folder and logs
        Dim args2() As String = {"-NoCleanup", "/NoCleanup"}
        If Environment.GetCommandLineArgs.Intersect(args2, StringComparer.OrdinalIgnoreCase).Any Then
            NoCleanup = True
        End If

        'Notify user that -NoCleanup was specified
        If NoCleanup = True Then
            MessageBox.Show("The -NoCleanup argument was specified, so the temp folder containing the files and logs will not be deleted.", "Notice", MessageBoxButtons.OK, MessageBoxIcon.Information)
        End If

        'Notify intro
        MessageBox.Show("Greetings! Please note that you MUST be connected to the Internet for this program to work.", "Important Notice", MessageBoxButtons.OK, MessageBoxIcon.Information)

        'Prep temp folder
        Functions.PrepareTempFolder()

        'Set props
        Label_TempPath.Text = TempPath
        Timer_AppUpdate.Enabled = True
    End Sub

    Private Sub Button_Go_Click(sender As Object, e As EventArgs) Handles Button_Go.Click
        Functions.Go()
    End Sub

    Private Sub Label_RootCertCabs_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles Label_RootCertCabs.LinkClicked
        Try
            Process.Start(Label_RootCertCabs.Text)
        Catch ex As Exception

        End Try
    End Sub

    Private Sub Label_DisallowedCertsCab_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles Label_DisallowedCertsCab.LinkClicked
        Try
            Process.Start(Label_DisallowedCertsCab.Text)
        Catch ex As Exception

        End Try
    End Sub

    Private Sub Timer_AppUpdate_Tick(sender As Object, e As EventArgs) Handles Timer_AppUpdate.Tick
        Timer_AppUpdate.Enabled = False

        If BackgroundWorker_AppUpdate.IsBusy = False Then BackgroundWorker_AppUpdate.RunWorkerAsync()
    End Sub
    Private Sub BackgroundWorker_AppUpdate_DoWork(sender As Object, e As DoWorkEventArgs) Handles BackgroundWorker_AppUpdate.DoWork
        Try
            Dim hasConnection As Boolean = My.Computer.Network.Ping("github.com")
            If hasConnection = False Then Throw New Exception("Cannot ping github.com")

            Dim wc As New WebClient()
            wc.Headers.Add("User-Agent", "UpdateRootCertificates")

            Dim json As String = wc.DownloadString("https://api.github.com/repos/asheroto/UpdateRootCertificates/releases/latest")
            Dim jObj As JObject = JObject.Parse(json)

            Dim latestVersionStr As String = jObj("tag_name").ToString().TrimStart("v"c)
            Dim latestVersion As New Version(latestVersionStr)
            Dim myVersion As New Version(My.Application.Info.Version.ToString)
            Dim result = latestVersion.CompareTo(myVersion)

            If result > 0 Then
                Dim assets = jObj("assets")
                Dim zipAsset = assets.FirstOrDefault(Function(a) a("name").ToString().ToLower().EndsWith("updaterootcertificates.zip"))

                If zipAsset IsNot Nothing Then
                    Dim downloadUrl As String = zipAsset("browser_download_url").ToString()

                    If Not String.IsNullOrWhiteSpace(downloadUrl) Then
                        Debug.WriteLine($"Download URL: {downloadUrl}")

                        Me.Invoke(Sub()
                                      Dim ask = MsgBox("Newer version available. Click OK to download the ZIP. The password is 'password'.", vbInformation + vbOKCancel)
                                      If ask = vbOK Then
                                          Dim x As New Process
                                          x.StartInfo.UseShellExecute = True
                                          x.StartInfo.FileName = downloadUrl
                                          x.StartInfo.WindowStyle = ProcessWindowStyle.Normal
                                          x.Start()
                                      End If
                                  End Sub)
                    End If
                End If
            Else
                Debug.WriteLine("No new version available")
            End If
        Catch ex As Exception
            ' Optional: log or handle error
        End Try
    End Sub


    Private Sub ThirdPartyLicenseInfo_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles ThirdPartyLicenseInfo.LinkClicked
        Try
            Process.Start("https://github.com/asheroto/UpdateRootCertificates/blob/master/LICENSE")
        Catch ex As Exception

        End Try
    End Sub

    Private Sub MoreInfoCTL_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles MoreInfoCTL.LinkClicked
        Try
            MsgBox("This program will update the Certificate Trust Lists on your computer. Root certificate lists have the hashes of the certificates and don't contain the 'actual' certificates themselves, HOWEVER, this is because when a Windows machine encounters a new certificate that is on the trust list that it hasn't seen before, it will automatically download the needed certificate behind-the-scenes (on demand). The reason we use Certificate Trust Lists instead of the 'actual' certificates is because Windows Update is required to generate the certificates using certutil. If Windows Update is enabled and in use, that means your root certificates would already be up-to-date as it handles root certificate updates automatically. Using this method, we're able to achieve our goal of having the latest root certificates without relying on Windows Update." + vbCrLf + vbCrLf + "Reference: https://bit.ly/ms-ctl-info", vbInformation, MoreInfoCTL.Text)
        Catch ex As Exception

        End Try
    End Sub

    Private Sub Label_TempPath_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles Label_TempPath.LinkClicked
        Try
            If Directory.Exists(Label_TempPath.Text) = False Then Exit Sub
            Shell($"explorer.exe ""{Label_TempPath.Text}""", AppWinStyle.NormalFocus)
        Catch ex As Exception

        End Try
    End Sub

    Private Sub Label_ReportIssue_LinkClicked(sender As Object, e As LinkLabelLinkClickedEventArgs) Handles Label_ReportIssue.LinkClicked
        Try
            Process.Start("https://github.com/asheroto/UpdateRootCertificates/issues")
        Catch ex As Exception

        End Try
    End Sub
End Class

Friend Class Functions
    ''' <summary>
    ''' Starts the process of updating the root certificate lists.
    ''' </summary>
    Friend Shared Sub Go()
        Try
            'Notify
            MessageBox.Show("Here we go... this process is super fast!", "Notice", MessageBoxButtons.OK, MessageBoxIcon.Information)

            'Disable button control
            MainWindow.Button_Go.Enabled = False

            'Download certs
            Functions.DownloadCerts()

            'expand
            Functions.ExtractCerts()

            'certutil
            Functions.Certutil()

            'Change button text
            MainWindow.Button_Go.Text = "ROOT CERTIFICATES UPDATED"

            'Delete temp folder
            Functions.DeleteTempFolder()

            'Notify
            MessageBox.Show("The root certificates lists were successfully downloaded and installed. Please restart the computer for changes to take effect. You may click OK and close the program now.", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information)
        Catch ex As Exception
            MessageBox.Show("An error has occurred." &
                            vbNewLine & vbNewLine & "Error message from the program:" & vbNewLine & ex.ToString & vbNewLine & vbNewLine &
                            "First try exiting the program and running it again. " &
                            "Look at the log files in the temp folder to help determine the issue. " &
                            "If you are missing log files for auth or dis, double-click the cab files to ensure they are not corrupted. " &
                            "You might also add this program to your list of AV exceptions if needed. " &
                            "Please report any issues by clicking ""Report Issue"".",
                            "Failure", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
            MainWindow.Button_Go.Enabled = True
            Exit Sub
        Finally
            'Activate window
            MainWindow.Activate()
        End Try
    End Sub

    ''' <summary>
    ''' Writes a log file to the temp folder.
    ''' </summary>
    ''' <param name="LogFileName"></param>
    ''' <param name="LogText"></param>
    Friend Shared Sub WriteLog(LogFileName As String, LogText As String)
        Try
            File.WriteAllText(Path.Combine(MainWindow.TempPath, LogFileName), LogText)
        Catch ex As Exception

        End Try
    End Sub

    ''' <summary>
    ''' Downloads certificates.
    ''' </summary>
    Friend Shared Sub DownloadCerts()
        'Download allowed certs
        Dim auth_url As String = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/authrootstl.cab"
        Dim auth_path As String = Path.Combine(MainWindow.TempPath, "authrootstl.cab")
        DownloadFile(auth_url, auth_path)

        'Download disallowed certs
        Dim dis_url As String = "http://ctldl.windowsupdate.com/msdownload/update/v3/static/trustedr/en/disallowedcertstl.cab"
        Dim dis_path As String = Path.Combine(MainWindow.TempPath, "disallowedcertstl.cab")
        DownloadFile(dis_url, dis_path)

        'Confirm downloaded files exist
        If File.Exists(auth_path) = False Then Throw New Exception("authrootstl.cab was not downloaded.")
        If File.Exists(dis_path) = False Then Throw New Exception("disallowedcertstl.cab was not downloaded.")
    End Sub

    ''' <summary>
    ''' Downloads a file from a URL to a specified path.
    ''' </summary>
    ''' <param name="URL">URL of the file to download.</param>
    ''' <param name="Path">Path to save the file to.</param>
    Friend Shared Sub DownloadFile(URL As String, Path As String)
        Dim client As New WebClient
        client.CachePolicy = New Cache.RequestCachePolicy(Cache.RequestCacheLevel.NoCacheNoStore)
        client.DownloadFile(URL, Path)
    End Sub

    ''' <summary>
    ''' Launches a command line process using ShellExecute and writes the output and errors to log files.
    ''' </summary>
    ''' <param name="FileName">Filename of the process to launch.</param>
    ''' <param name="Arguments">Arguments to pass to the process.</param>
    ''' <param name="OutputFileName">Filename of the log file to write the output to.</param>
    ''' <param name="ErrorsFileName">Filename of the log file to write the errors to.</param>
    Friend Shared Sub LaunchProcess(FileName As String, Arguments As String, OutputFileName As String, ErrorsFileName As String)
        Dim proc As New Process
        With proc.StartInfo
            .CreateNoWindow = True ' Don't create a window
            .WorkingDirectory = MainWindow.TempPath
            .FileName = FileName
            .Arguments = Arguments

            'Redirect output and errors
            .UseShellExecute = False  ' Required for redirection
            .RedirectStandardOutput = True  ' Redirect standard output
            .RedirectStandardError = True  ' Redirect standard error
        End With

        'Start process
        proc.Start()

        'Read output and errors
        Dim output As String = proc.StandardOutput.ReadToEnd()  ' Read the output
        Dim errors As String = proc.StandardError.ReadToEnd()  ' Read the errors

        'Wait for process to finish
        proc.WaitForExit()

        'Write output and errors to log
        Functions.WriteLog(OutputFileName, output)
        Functions.WriteLog(ErrorsFileName, errors)
    End Sub

    ''' <summary>
    ''' Extract certificates from cab archives using "expand" command
    ''' </summary>
    Friend Shared Sub ExtractCerts()
        'auth: Start authroot process
        LaunchProcess("expand.exe", "authrootstl.cab -R .\", "expand_auth_output.txt", "expand_auth_errors.txt")

        'dis: Initialize disallowed process
        LaunchProcess("expand.exe", "disallowedcertstl.cab -R .\", "expand_dis_output.txt", "expand_dis_errors.txt")

        'Confirm extracted files exist
        Dim authroot_stl As String = Path.Combine(MainWindow.TempPath, "authroot.stl")
        Dim disallowedcert_stl As String = Path.Combine(MainWindow.TempPath, "disallowedcert.stl")
        If File.Exists(authroot_stl) = False Then Throw New Exception("authroot.stl was not extracted.")
        If File.Exists(disallowedcert_stl) = False Then Throw New Exception("disallowedcert.stl was not extracted.")
    End Sub

    ''' <summary>
    ''' Run certutil to apply certificates
    ''' </summary>
    Friend Shared Sub Certutil()
        'auth: Initialize authroot process
        LaunchProcess("certutil.exe", "-addstore -f root authroot.stl", "certutil_auth_output.txt", "certutil_auth_errors.txt")

        'dis: Initialize disallowed process
        LaunchProcess("certutil.exe", "-addstore -f disallowed disallowedcert.stl", "certutil_dis_output.txt", "certutil_dis_errors.txt")
    End Sub

    ''' <summary>
    ''' Deletes the temporary folder.
    ''' </summary>
    Friend Shared Sub DeleteTempFolder()
        Try
            'If NoCleanup is enabled, exit sub
            If MainWindow.NoCleanup Then Exit Sub

            'Delete temp folder
            Directory.Delete(MainWindow.TempPath, True)

            'Disable Label_TempPath
            MainWindow.Label_TempPath.Enabled = False
        Catch ex As Exception

        End Try
    End Sub

    ''' <summary>
    ''' Generates and returns a temporary folder name under the %temp% directory.
    ''' </summary>
    ''' <returns></returns>
    Friend Shared Function CreateTempFolderString()
        Dim r As New Random
        Return Path.GetTempPath & "RCU_" & r.Next(1000, 1000000).ToString
    End Function

    ''' <summary>
    ''' Creates the temporary folder if it does not exist.
    ''' </summary>
    Friend Shared Sub PrepareTempFolder()
        Try
            'Generate temp folder name
            MainWindow.TempPath = CreateTempFolderString()

            'If temp folder does not exist, create it
            If Directory.Exists(MainWindow.TempPath) = False Then
                'Create temp folder
                Directory.CreateDirectory(MainWindow.TempPath)
            Else
                'Regenerate temp folder name
                MainWindow.TempPath = CreateTempFolderString()

                'Create temp folder
                Directory.CreateDirectory(MainWindow.TempPath)
            End If
        Catch ex As Exception
            MessageBox.Show($"An error has occurred when creating the temporary folder. Please make sure you have the appropriate permissions to create a directory under %temp% such as {MainWindow.TempPath}", "Failure", MessageBoxButtons.OK, MessageBoxIcon.Exclamation)
            Environment.Exit(1)
        End Try
    End Sub
End Class

Friend Class API
    Private m_version_number As String

    ''' <summary>
    ''' Gets or sets the version number.
    ''' </summary>
    ''' <returns></returns>
    Friend Property version_number As String
        Get
            Return m_version_number
        End Get
        Set(value As String)
            m_version_number = value
        End Set
    End Property

    Private m_download_url As String

    ''' <summary>
    ''' Gets or sets the download URL.
    ''' </summary>
    ''' <returns></returns>
    Friend Property download_url As String
        Get
            Return m_download_url
        End Get
        Set(value As String)
            m_download_url = value
        End Set
    End Property
End Class