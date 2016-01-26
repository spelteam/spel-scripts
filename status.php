<?php
  echo "<!DOCTYPE html>";
  echo "<html>";
    echo "<head>";
      echo "<title>SPEL Status</title>";
      echo "<style>";
        echo "td.OK { background-color:#00FF00 }";
        echo "td.FAILED { background-color:#FF0000 }";
        echo "tr.OK { background-color:#00FF00 }";
        echo "tr.FAILED { background-color:#FF0000 }";
      echo "</style>";
    echo "</head>";
    echo "<body>";
      echo '<h1 align="center">SPEL Status</h1>';
      $db_connect = mysql_connect("localhost", "root", 'XXXXXX') or die ("Couldn't connect: " . mysql_error());
      mysql_select_db("pose_mediawiki", $db_connect)  or die ("Couldn't switch the working place: " . mysql_error());
      echo '<h2 align="center">Summary</h2>';
      $result = mysql_query("select res.*, case when res.failed=0 then 'OK' else 'FAILED' end as summary from (select 'Linux' as resultname, (select count(*) from unittests where linux=1) as ok, (select count(*) from unittests where linux=0) as failed union all select 'Windows' as resultname, (select count(*) from unittests where windows=1) as ok, (select count(*) from unittests where windows=0) as failed union all select 'Total' as resultname, (select count(*) from unittests where linux=1 and windows=1) as ok, (select count(*) from unittests where linux=0 or windows=0) as failed) res;") or die (mysql_error());
      echo '<table align="center" border="1">';
        echo '<thead>';
          echo '<tr>';
            echo '<th>Result</th>';
            echo '<th>OK</th>';
            echo '<th>FAILED</th>';
          echo '</tr>';
        echo '</thead>';
        echo '<tbody>';
        while ($data = mysql_fetch_array($result))
        {
          echo '<tr class="' . $data['summary'] .'">';
            echo '<td>' . $data['resultname'] . '</td>';
            echo '<td>' . $data['ok'] . '</td>';
            echo '<td>' . $data['failed'] . '</td>';
          echo '</tr>';
        }
        echo '</tbody>';
      echo '</table>';
      echo '<h2 align="center">Detailed</h2>';
      $result = mysql_query("select testname, case when linux=1 then 'OK' else 'FAILED' end as linux, case when windows=1 then 'OK' else 'FAILED' end as windows, case when linux=1 and windows=1 then 'OK' else 'FAILED' end as summary from unittests order by testname;") or die (mysql_error());
      echo '<table align="center" border="1">';
        echo '<thead>';
          echo '<tr>';
            echo '<th>Test Name</th>';
            echo '<th>Linux Result</th>';
            echo '<th>Windows Result</th>';
          echo '</tr>';
        echo '</thead>';
        echo '<tbody>';
        while ($data = mysql_fetch_array($result))
        {
          echo '<tr>';
            echo '<td class="' . $data['summary'] . '">' . $data['testname'] . '</td>';
            echo '<td class="' . $data['linux'] . '">' . $data['linux'] . '</td>';
            echo '<td class="' . $data['windows'] .'">' . $data['windows'] . '</td>';
          echo '</tr>';
        }
        echo '</tbody>';
      echo '</table>';
      mysql_close($db_connect);
    echo "</body>";
  echo "</html>";
?>
