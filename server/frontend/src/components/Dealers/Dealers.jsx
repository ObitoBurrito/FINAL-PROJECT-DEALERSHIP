import React, { useState, useEffect } from 'react';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';
import review_icon from "../assets/reviewicon.png";

const Dealers = () => {
  const [dealersList, setDealersList] = useState([]);
  const [states, setStates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  // Base endpoints
  const dealer_url = "/djangoapp/get_dealers";
  const dealer_url_by_state = (st) => `/djangoapp/get_dealers/${encodeURIComponent(st)}`;

  const filterDealers = async (state) => {
    setLoading(true);
    setErr("");
    try {
      // "All" should NOT hit /All
      const url = !state || state === "All" ? dealer_url : dealer_url_by_state(state);
      const res = await fetch(url, { method: "GET", credentials: "include" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const retobj = await res.json();
      if (retobj.status === 200) {
        setDealersList(Array.from(retobj.dealers || []));
      } else {
        setDealersList([]);
        setErr("Unexpected response status");
      }
    } catch (e) {
      setDealersList([]);
      setErr(`Failed to load dealers: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const get_dealers = async () => {
    setLoading(true);
    setErr("");
    try {
      const res = await fetch(dealer_url, { method: "GET", credentials: "include" });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const retobj = await res.json();
      if (retobj.status === 200) {
        const all_dealers = Array.from(retobj.dealers || []);
        setDealersList(all_dealers);

        const uniqueStates = Array.from(
          new Set(all_dealers.map(d => d.state).filter(Boolean))
        ).sort();
        setStates(uniqueStates);
      } else {
        setDealersList([]);
        setStates([]);
        setErr("Unexpected response status");
      }
    } catch (e) {
      setDealersList([]);
      setStates([]);
      setErr(`Failed to load dealers: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    get_dealers();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const isLoggedIn = sessionStorage.getItem("username") != null;

  return (
    <div>
      <Header/>

      <table className='table'>
        <thead>
          <tr>
            <th>ID</th>
            <th>Dealer Name</th>
            <th>City</th>
            <th>Address</th>
            <th>Zip</th>
            <th>
              <select
                name="state"
                id="state"
                defaultValue=""                 // React-friendly placeholder
                onChange={(e) => filterDealers(e.target.value)}
              >
                <option value="" disabled hidden>State</option>
                <option value="All">All States</option>
                {states.map((state) => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </th>
            {isLoggedIn ? <th>Review Dealer</th> : null}
          </tr>
        </thead>

        <tbody>
          {loading && (
            <tr><td colSpan={isLoggedIn ? 7 : 6}>Loading…</td></tr>
          )}
          {!loading && dealersList.length === 0 && !err && (
            <tr><td colSpan={isLoggedIn ? 7 : 6}>No dealers found.</td></tr>
          )}
          {!loading && err && (
            <tr><td colSpan={isLoggedIn ? 7 : 6} style={{color:'#b00'}}>{err}</td></tr>
          )}

          {!loading && !err && dealersList.map((dealer, idx) => {
            const id = dealer['id'] ?? dealer['dealerId'] ?? idx;
            const name = dealer['full_name'] ?? dealer['name'] ?? 'Unnamed';
            return (
              <tr key={id}>
                <td>{id}</td>
                <td><a href={'/dealer/'+id}>{name}</a></td>
                <td>{dealer['city'] ?? ''}</td>
                <td>{dealer['address'] ?? ''}</td>
                <td>{dealer['zip'] ?? ''}</td>
                <td>{dealer['state'] ?? ''}</td>
                {isLoggedIn ? (
                  <td>
                    <a href={`/postreview/${id}`}>
                      <img src={review_icon} className="review_icon" alt="Post Review"/>
                    </a>
                  </td>
                ) : null}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default Dealers;
