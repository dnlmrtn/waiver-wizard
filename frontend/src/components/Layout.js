import { Outlet } from 'react-router-dom';
import '../static/App.css';
const Layout = () => {
    return (
        <div>
            <div className='content-container' style={{ backgroundColor: "#1b1c22" }}>
                <div className="content">
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default Layout;
