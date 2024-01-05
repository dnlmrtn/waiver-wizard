import { Outlet } from 'react-router-dom';
import '../static/App.css';
const Layout = () => {
    return (
        <div>
            <div className="content">
                <Outlet />
            </div>
        </div>
    );
};

export default Layout;
