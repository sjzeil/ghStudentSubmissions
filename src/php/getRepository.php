<!DOCTYPE html>
<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

include 'configuration.php';
?>
<html>
    <head>
        <title>
            <?php
                $asst = $_REQUEST["asst"];
                echo $courseName + ' ' + $asst;
            ?>
        </title>
    </head>
    <body>
        <h1>
            Starting Code for 
            <?php
                $asst = $_REQUEST["asst"];
                echo "{$courseName}  {$asst}";
            ?>
        </h1>
	  <?php
        if ($asst == NULL || $asst == "") {
            echo "<p>Missing asst parameter</p>";
            $asst = 'missing';
        }
        $username = $_SERVER['REMOTE_USER'] ?? "unknown";
        $githubAccount = '';
        echo $username;
        
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
        }
            
        echo "<p>githubAccount is {$githubAccount}</p>";

	   ?>
	   <h1>
            <?php
                //echo $courseName: $asst repository;
            ?>
		</h1>
        <!--
		<p>
				<form action="registerRepo.php" method="post">
				  <input type="hidden" name='asst' id='asst' value="<?php echo $asst; ?>"/>
				  <input type="hidden" name='asstsDir' id='asstsDir' value="<?php echo $asstsDir; ?>"/>
				  <input type="hidden" name='gradeDir' id='gradeDir' value="<?php echo $gradeDir; ?>"/>
				  <p>
					<label for="repoURL"><b>Repository SSH URL: </b></label>
					<input type="text" id="repoURL" name="repoURL" size="40" 
						value="<?php echo $repoURL; ?>"/>
				  </p>
				</form>
        </p>
    -->
    </body>
</html>
