<?php

    $req = $_GET['req'];

    $auth_users =  array(
        "Maksi1999" => md5("salt_req" . "Maksi1999")
    );

    $username = array_search($req, $auth_users);

    header('Content-Type: application/json');
    if ($username) {
        header('Content-Type: application/json');
        http_response_code(200);
        $data = array( 'res' => md5("salt_res" . $username));
    } else {
        http_response_code(403);
        $data = array( 'res' => False);
    }
    echo json_encode($data);
 
?>