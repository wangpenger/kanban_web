function goto_func(id)
{
    switch(id)
    {
        case 1:
        {
            window.location = "kanban";
            break;
        }
        case 2:
        {
            window.location = "burndown";
            break;
        }
        case 3:
        {
            window.location = "yesterday_did";
            break;
        }
        case 4:
        {
            window.location = "setting";
            window.location = "action_error?info=Only for administrator!";
            break;
        }
        default:
        {
            window.location = "kanban";
            break;
        }
    }
}