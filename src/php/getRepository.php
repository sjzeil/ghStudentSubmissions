<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include 'configuration.php';
include 'header.php';

function curl_get($endpoint) {
    $headers = [
        "User-Agent: ghSubmissions",
        "Authorization: token {$_SESSION['accessToken']}"
    ];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_URL, "https://api.github.com/{$endpoint}");
    
    $raw_response = curl_exec($ch);
    curl_close($ch);

    $response = json_decode($raw_response); 
    return $response;
}


function curl_post($endpoint, $options) {
    $headers = [
        "User-Agent: ghSubmissions",
        "Authorization: token {$_SESSION['accessToken']}",
        "Accept: application/vnd.github+json",
        "Content-Type: application/json"
    ];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_URL, "https://api.github.com/{$endpoint}");

    $jsonData = json_encode($options);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
    
    $raw_response = curl_exec($ch);
    $httpStatusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if (curl_errno($ch)) {
        $message = 'Error from cURL: ' . curl_error($ch);
        echo "<p>{$message}</p>";
        $response = ['message' => $message];
    } else {
        $response = json_decode($raw_response, true);  
        if ($httpStatusCode != 201) {
            echo "<p>Error {$httpStatusCode}: " . ($response['message'] ?? 'Unknown error')  . '</p>';
        }
    }
    curl_close($ch);

    return $response;
}


function curl_put($endpoint, $options) {
    $headers = [
        "User-Agent: ghSubmissions",
        "Authorization: token {$_SESSION['accessToken']}",
        "Accept: application/vnd.github+json",
        "Content-Type: application/json"
    ];
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_URL, "https://api.github.com/{$endpoint}");

    $jsonData = json_encode($options);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $jsonData);
    
    $raw_response = curl_exec($ch);
    $httpStatusCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);

    if (curl_errno($ch)) {
        $message = 'Error from cURL: ' . curl_error($ch);
        echo "<p>{$message}</p>";
        $response = ['message' => $message];
    } else {
        $response = json_decode($raw_response, true); 
        if ($httpStatusCode == 204) {
            // This error seems to be returned, with no explanation, even when the
            // operation succeeds.  
            $response = ['httpCode' => '204'];
        }else if ($httpStatusCode != 201) {
            if ($response == NULL) {
                $response = ['message' => "Error {$httpStatusCode}: (no explanation from Github)"];
            }
            echo "<p>Error {$httpStatusCode}: " . ($response['message'] ?? 'Unknown error')  . '</p>';
        }
    }
    curl_close($ch);

    return $response;
}





$username = $_SERVER['REMOTE_USER'] ?? "unknown";

session_start();

$step = isset($_POST['step']) ? (int)$_POST['step'] : 1;

if (isset($_POST['cancel'])) {
    $step = 99;
}

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    switch ($step - 1) { // process the data posted by the prior step}
        case 1:
            $suggestedAccountName = $_POST['githubAccount'];
            $cleanSuggestion = preg_replace('/[^-a-zA-Z0-9]/', '', $suggestedAccountName);
            $_SESSION['githubAccount'] = $cleanSuggestion;
            break;
        case 2:
            break;
        case 4:
            $_SESSION['assignmentName'] = $_POST['assignments'];
            break;
        default:
            break;
    }
}

if ($step == 1) {
    if (($handle = fopen("{$courseDirectory}/.github", "r")) !== FALSE) {
        $accessToken = rtrim(fgets($handle));
        $_SESSION['accessToken'] = $accessToken;
        fclose($handle);
    } else {
            echo "Could not read {$courseDirectory}/.github";
    }

    $githubAccount = '';
    
    if (($handle = fopen("{$courseDirectory}/students.csv", "r")) !== FALSE) {
        // Loop through each row of the CSV file
        while (($row = fgetcsv($handle, 0, ",")) !== FALSE) {
            // $row is an array of columns for the current line
            if ($row[0] == $username) {
                $githubAccount = $row[1];
                break;
            }
        }
        
        // Close the file stream
        fclose($handle);
    } else {
            echo "Could not read from {$courseDirectory}/students.csv";
    }

        
    if ($githubAccount != null && $githubAccount != '') {
        echo "<p>Found Github account for student {$username}: {$githubAccount}</p>";
        $_SESSION['githubAccount'] = htmlspecialchars($githubAccount);
        $step = 4;
    }
} 

if ($step == 2) {
    $response = curl_get("users/{$_SESSION['githubAccount']}");
    if (property_exists($response, 'message')) {
        $message = $response->message;
    } else {
        $newStudent = [$username, $_SESSION['githubAccount']];
        if (($handle = fopen("{$courseDirectory}/students.csv", "a")) !== FALSE) {
            if (flock($handle, LOCK_EX)) { 
                fputcsv($handle, $newStudent);
            } else {
            echo "Could not lock {$courseDirectory}/students.csv";    
            }
            // Close the file stream
            fclose($handle);
        } else {
            echo "Could not write to {$courseDirectory}/students.csv";
        }
        $step = 4;
    }

}

// if ($step == 3) {
//     echo "";
// } 

if ($step == 4) {
    $assignmentNames = [];
    if (($handle = fopen("{$courseDirectory}/assignments.csv", "r")) !== FALSE) {
        // Loop through each row of the CSV file
        $headers = fgetcsv($handle, 0, ",");
        while (($row = fgetcsv($handle, 0, ",")) !== FALSE) {
            // $row is an array of columns for the current line
            $assignmentNames[] = $row[0];
        }
        
        // Close the file stream
        fclose($handle);
    } else {
            echo "Could not read from {$courseDirectory}/assignments.csv";
    }
}

if ($step == 5) {
    if (($handle = fopen("{$courseDirectory}/assignments.csv", "r")) !== FALSE) {
        // Loop through each row of the CSV file
        $headers = fgetcsv($handle, 0, ",");
        while (($row = fgetcsv($handle, 0, ",")) !== FALSE) {
            if ($row[0] == $_SESSION['assignmentName']) {
                $assignmentName = $row[0];
                $templateRepoName = $row[1];
                if (count($row) >= 3) {
                    $permissions = $row[2];
                } else {
                    $permissions = "push";
                }
                if (count($row) >= 4) {
                    $teamGroup = $row[3];
                } else {
                    $teamGroup = "";
                }
                break;
            }
        }
        // Close the file stream
        fclose($handle);
    } else {
            echo "Could not read from {$courseDirectory}/assignments.csv";
    }    
    if (($handle = fopen("{$courseDirectory}/repositories.csv", "r")) !== FALSE) {
        // Loop through each row of the CSV file
        $headers = fgetcsv($handle, 0, ",");
        $repoName = '';
        $url = '';
        while (($row = fgetcsv($handle, 0, ",")) !== FALSE) {
            if ($row[0] == $_SESSION['assignmentName']
                && $row[1] == $username) {
                    $repoName = $row[2];
                    $url = "https://github.com/{$repoName}/";
                    $message = "{$username} has a repository for assignment '{$row[0]}' at <a href='{$url}' target='blank'>$url</a>.";
                    break;
            }
        }
        // Close the file stream
        fclose($handle);
        
        if ($url == '') {
            // echo "<p>Need to create repo {$assignmentName} {$templateRepoName} {$permissions} {$teamGroup}</p>";
            $templateNameParts = explode('/', $templateRepoName);
            $organization = $templateNameParts[0];
            $githubAccount = $_SESSION['githubAccount'];
            $newTemplateName = "{$courseName}--{$assignmentName}--{$githubAccount}";
            $newTemplateName = preg_replace('/  */','_', $newTemplateName);
            $newTemplateName = preg_replace('/[^-_a-zA-Z0-9]/', '', $newTemplateName);
            $options = [
                'owner' => $organization,
                'name' => $newTemplateName,       // Required: Name of the repository
                'description' => "{$courseName} {$assignmentName},  created for {$githubAccount} from template {$newTemplateName}", // Optional description
                'private' => true,                 // true = Private, false = Public
                'include_all_branches' => false
            ];
            $endpoint = "repos/{$templateRepoName}/generate";
            $response = curl_post($endpoint, $options);
            //var_dump($response);
            if (!array_key_exists('message', $response)) {
                $actualTemplateName = $response['name'];
                $options = [
                    'permissions' => $permissions
                ];
                $endpoint = "repos/{$organization}/{$actualTemplateName}/collaborators/{$githubAccount}";
                $response = curl_put($endpoint, $options);
                //var_dump($response);
                if (!array_key_exists('message', $response)) {
                    if (($handle = fopen("{$courseDirectory}/repositories.csv", "a")) !== FALSE) {
                        $timeStamp = date('c');
                        $newRepository = [$assignmentName, $username, "{$organization}/{$actualTemplateName}", $timeStamp];
                        if (flock($handle, LOCK_EX)) { 
                                fputcsv($handle, $newRepository);
                        } else {
                        echo "Could not lock {$courseDirectory}/repositories.csv";    
                        }
                        // Close the file stream
                        fclose($handle);
                    } else {
                        echo "Could not write to {$courseDirectory}/repositories.csv";
                    }
                    $url = "https://github.com/${organization}/{$actualTemplateName}/";
                    echo "<p>New repository created at <a href='{$url}' target='_blank'>{$url}</a></p>";
                }
            }
        } else {
            echo "<p>{$message}</p>";
        }
    } else {
            echo "Could not read from {$courseDirectory}/repositories.csv";
    }    


} 

if ($step > 5 || $step < 1) {
    echo "<p>Canceled</p>";
    session_unset();
    session_destroy();
}
    
switch ($step) {
case 1:
    ?>
    <h2>Register Your Github Account</h2>
    <form method = "POST" action = "">
        <label for='githubAccount'>Login name for your Github Account:</label>
        <input type="text" id="githubAccount" name="githubAccount" width="16" required> <br/>
        <input type="hidden" name="step" value="2"/>
        <table>
            <tr><td>
                <button type="submit" name="step1">Register</button>
            </td><td>
                <button type="submit" name="cancel">Cancel</button>
            </td></tr>
        </table>
    </form>
    <?php
    break;
case 2:
    ?>
    <h2>Invalid Github Account Name</h2>
    <p>'<?= $_SESSION['githubAccount'] ?>' does not appear to be a valid Github login name. (<?= $message ?>)</p>
    <form method = "POST" action = "">
        <input type="hidden" name="step" value="1"/>
        <button type="submit" name="step2">Try Again</button>
    </form>
    <?php
    break;
case 3:
    ?>

    <form method = "POST" action = "">
        <input type="hidden" name="step" value="4"/>
        <button type="submit" name="step3">Next step</button>
    </form>
    <?php
    break;
case 4:
    ?>
    <form method = "POST" action = "">
        <label for='assignments'>Choose an assignment:</label>
        <input type="hidden" name="step" value="5"/>
        <select name='assignments' id='assignments' required>
            <option value="" disabled selected hidden>Select...</option>
        <?php
        foreach ($assignmentNames as $asst) {
            echo "<option value=\"{$asst}\">{$asst}</option>\n";
        }
        ?>
        </select>
        <br/>
        <table>
            <tr><td>
                <button type="submit" name="step4">Select</button>
            </td><td>
                <button type="submit" name="cancel">Cancel</button>
            </td></tr>
        </table>
    </form>
    <?php
    break;
default:
    ?>
    <form method = "POST" action = "">
            <input type="hidden" name="step" value="1"/>
            <button type="submit" name="step99">Finish</button>
    </form>

<?php
}
?>
      </main>
    </body>
</html>
