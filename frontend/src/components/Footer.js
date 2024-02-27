import React from 'react';
import '../static/App.css'
import '../static/Footer.css'


const Footer = () => {

    return (
        <div className='footer-container'>

            <div className='footer-notes'>
                Notes:
                <li >
                    Player injuries within the last 3 days are bold
                </li>
                <li >

                </li>
                <li >
                    Player status is updated every 10 minutes between 4:30pm to 10pm EST. Keep an eye out for changes
                </li>
            </div>
        </div>
    );
};

export default Footer;